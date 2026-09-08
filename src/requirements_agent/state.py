"""Shared LangGraph state for the requirements collection workflow."""

from operator import add
from typing import Annotated, Literal, TypedDict

from requirements_agent.schemas import (
    CoverageAssessment,
    FinalSpecification,
    Requirement,
    Stakeholder,
    ValidationIssue,
)


class ConversationTurn(TypedDict):
    """One human or agent message preserved in graph state."""

    role: Literal["stakeholder", "agent"]
    content: str


class AgentState(TypedDict):
    """Shared state passed between LangGraph nodes."""

    project_idea: str

    conversation_history: Annotated[list[ConversationTurn], add]

    stakeholders: list[Stakeholder]
    collected_requirements: list[Requirement]
    assumptions: list[str]

    coverage: list[CoverageAssessment]
    open_questions: list[str]

    validation_issues: list[ValidationIssue]

    clarification_round: int
    max_clarification_rounds: int

    ready_for_validation: bool
    validation_passed: bool

    final_specification: FinalSpecification | None


def create_initial_state(
    project_idea: str,
    max_clarification_rounds: int = 3,
) -> AgentState:
    """Create the initial state for a requirements collection session."""

    if not project_idea.strip():
        raise ValueError("project_idea cannot be empty")

    return AgentState(
        project_idea=project_idea.strip(),
        conversation_history=[
            {
                "role": "stakeholder",
                "content": project_idea.strip(),
            }
        ],
        stakeholders=[],
        collected_requirements=[],
        assumptions=[],
        coverage=[],
        open_questions=[],
        validation_issues=[],
        clarification_round=0,
        max_clarification_rounds=max_clarification_rounds,
        ready_for_validation=False,
        validation_passed=False,
        final_specification=None,
    )