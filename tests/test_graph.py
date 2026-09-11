"""Tests for LangGraph requirements workflow."""

from langgraph.types import Command

from requirements_agent.graph import build_graph
from requirements_agent.schemas import (
    CoverageAssessment,
    CoverageStatus,
)
from requirements_agent.state import create_initial_state


def fake_analyzer(state):
    """Return incomplete first-round data and sufficient second-round data."""

    if state["clarification_round"] == 0:
        return {
            "coverage": [
                CoverageAssessment(
                    category="actors",
                    status=CoverageStatus.PARTIAL,
                ),
                CoverageAssessment(
                    category="functional",
                    status=CoverageStatus.PARTIAL,
                ),
            ],
            "open_questions": [
                "How should students authenticate?"
            ],
        }

    categories = [
        "actors",
        "functional",
        "non_functional",
        "data",
        "security",
        "constraints",
        "dependencies",
    ]

    return {
        "coverage": [
            CoverageAssessment(
                category=category,
                status=CoverageStatus.PARTIAL,
            )
            for category in categories
        ],
        "open_questions": [],
    }


def test_graph_pauses_and_resumes_for_clarification() -> None:
    graph = build_graph(analyzer=fake_analyzer)

    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    config = {
        "configurable": {
            "thread_id": "test-thread"
        }
    }

    first_result = graph.invoke(
        state,
        config=config,
    )

    assert "__interrupt__" in first_result

    final_result = graph.invoke(
        Command(
            resume="Students authenticate using university SSO."
        ),
        config=config,
    )

    assert final_result["clarification_round"] == 1
    assert final_result["ready_for_validation"] is True

    assert (
        final_result["conversation_history"][-1]["content"]
        == "Students authenticate using university SSO."
    )