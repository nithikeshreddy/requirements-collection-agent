"""Tests for human clarification interactions."""

import pytest

from requirements_agent.interaction import record_clarification_response
from requirements_agent.state import create_initial_state


def test_record_clarification_response() -> None:
    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    state["open_questions"] = [
        "How should students authenticate?",
        "Can students cancel reservations?",
    ]

    updated_state = record_clarification_response(
        state,
        "Students use university SSO and can cancel reservations.",
    )

    assert updated_state["clarification_round"] == 1

    assert len(updated_state["conversation_history"]) == 3

    assert updated_state["conversation_history"][1]["role"] == "agent"
    assert "How should students authenticate?" in (
        updated_state["conversation_history"][1]["content"]
    )

    assert updated_state["conversation_history"][2] == {
        "role": "stakeholder",
        "content": (
            "Students use university SSO and can cancel reservations."
        ),
    }


def test_empty_clarification_response_is_rejected() -> None:
    state = create_initial_state("Build a room reservation application.")

    state["open_questions"] = [
        "How should students authenticate?"
    ]

    with pytest.raises(ValueError):
        record_clarification_response(state, "   ")


def test_response_without_open_questions_is_rejected() -> None:
    state = create_initial_state("Build a room reservation application.")

    with pytest.raises(ValueError):
        record_clarification_response(
            state,
            "Students use university SSO.",
        )