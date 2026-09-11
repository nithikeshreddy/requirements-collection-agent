"""LangGraph workflow for iterative requirements collection."""

from collections.abc import Callable
from typing import Literal

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from requirements_agent.completeness import requirements_ready_for_validation
from requirements_agent.nodes.analyze import analyze_requirements
from requirements_agent.schemas import (
    CoverageAssessment,
    CoverageStatus,
    Requirement,
    RequirementCategory,
    Stakeholder,
)
from requirements_agent.state import AgentState


def assess_completeness(state: AgentState) -> dict:
    """Apply deterministic requirements-completeness rules."""

    return {
        "ready_for_validation": requirements_ready_for_validation(state)
    }


def route_after_completeness(
    state: AgentState,
) -> Literal["collect_clarification", "validation_ready"]:
    """Choose the next workflow step."""

    if state["ready_for_validation"]:
        return "validation_ready"

    return "collect_clarification"


def collect_clarification(state: AgentState) -> dict:
    """Pause execution and request clarification from the stakeholder."""

    if not state["open_questions"]:
        raise ValueError(
            "Clarification is required but no open questions are available."
        )

    formatted_questions = "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(state["open_questions"], start=1)
    )

    response = interrupt(
        {
            "type": "requirements_clarification",
            "round": state["clarification_round"] + 1,
            "questions": state["open_questions"],
        }
    )

    if not isinstance(response, str) or not response.strip():
        raise ValueError("Clarification response cannot be empty.")

    return {
        "conversation_history": [
            {
                "role": "agent",
                "content": f"Clarification questions:\n{formatted_questions}",
            },
            {
                "role": "stakeholder",
                "content": response.strip(),
            },
        ],
        "clarification_round": state["clarification_round"] + 1,
    }


def validation_ready(state: AgentState) -> dict:
    """Placeholder boundary for the validation stage."""

    return {}

def create_checkpointer() -> InMemorySaver:
    """Create a checkpoint saver with explicitly allowed application types."""

    serializer = JsonPlusSerializer(
        allowed_msgpack_modules=[
            Stakeholder,
            Requirement,
            RequirementCategory,
            CoverageAssessment,
            CoverageStatus,
        ]
    )

    return InMemorySaver(serde=serializer)


def build_graph(
    analyzer: Callable[[AgentState], dict] = analyze_requirements,
):
    """Build the requirements-collection LangGraph."""

    builder = StateGraph(AgentState)

    builder.add_node("analyze_requirements", analyzer)
    builder.add_node("assess_completeness", assess_completeness)
    builder.add_node("collect_clarification", collect_clarification)
    builder.add_node("validation_ready", validation_ready)

    builder.add_edge(START, "analyze_requirements")

    builder.add_edge(
        "analyze_requirements",
        "assess_completeness",
    )

    builder.add_conditional_edges(
        "assess_completeness",
        route_after_completeness,
        {
            "collect_clarification": "collect_clarification",
            "validation_ready": "validation_ready",
        },
    )

    builder.add_edge(
        "collect_clarification",
        "analyze_requirements",
    )

    builder.add_edge(
        "validation_ready",
        END,
    )

    return builder.compile(
    checkpointer=create_checkpointer()
)