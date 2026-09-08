"""Tests for LangGraph agent state."""

import pytest

from requirements_agent.state import create_initial_state


def test_create_initial_state() -> None:
    idea = "Build an application where students can reserve study rooms."

    state = create_initial_state(idea)

    assert state["project_idea"] == idea
    assert state["clarification_round"] == 0
    assert state["max_clarification_rounds"] == 3
    assert state["ready_for_validation"] is False
    assert state["validation_passed"] is False
    assert state["final_specification"] is None

    assert state["conversation_history"] == [
        {
            "role": "stakeholder",
            "content": idea,
        }
    ]


def test_empty_project_idea_is_rejected() -> None:
    with pytest.raises(ValueError):
        create_initial_state("   ")