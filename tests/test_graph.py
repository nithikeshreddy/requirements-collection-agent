"""Tests for LangGraph requirements workflow."""

from langgraph.types import Command

from requirements_agent.graph import build_graph
from requirements_agent.schemas import (
    CoverageAssessment,
    CoverageStatus,
    ValidationIssue,
    ValidationIssueType,
)
from requirements_agent.state import create_initial_state


def complete_coverage() -> list[CoverageAssessment]:
    """Return sufficient coverage for validation."""

    categories = [
        "actors",
        "functional",
        "non_functional",
        "data",
        "security",
        "constraints",
        "dependencies",
    ]

    return [
        CoverageAssessment(
            category=category,
            status=CoverageStatus.PARTIAL,
        )
        for category in categories
    ]


def fake_analyzer(state):
    """Require one collection clarification before validation."""

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

    return {
        "coverage": complete_coverage(),
        "open_questions": [],
    }


def passing_validator(state):
    """Simulate successful validation."""

    return {
        "validation_issues": [],
        "validation_passed": True,
        "open_questions": [],
    }


def test_graph_pauses_then_reaches_validation() -> None:
    graph = build_graph(
        analyzer=fake_analyzer,
        validator=passing_validator,
    )

    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    config = {
        "configurable": {
            "thread_id": "validation-pass-thread"
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
    assert final_result["validation_passed"] is True
    assert final_result["validation_issues"] == []


def validator_with_issue_then_pass(state):
    """Fail validation first, then pass after clarification."""

    if state["clarification_round"] < 2:
        issue = ValidationIssue(
            issue_type=ValidationIssueType.TESTABILITY,
            severity="medium",
            description="Performance requirement is not measurable.",
            clarification_question=(
                "What response-time target should the system meet?"
            ),
        )

        return {
            "validation_issues": [issue],
            "validation_passed": False,
            "open_questions": [
                "What response-time target should the system meet?"
            ],
        }

    return {
        "validation_issues": [],
        "validation_passed": True,
        "open_questions": [],
    }


def test_validation_failure_returns_to_clarification() -> None:
    graph = build_graph(
        analyzer=fake_analyzer,
        validator=validator_with_issue_then_pass,
    )

    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    config = {
        "configurable": {
            "thread_id": "validation-loop-thread"
        }
    }

    first_result = graph.invoke(
        state,
        config=config,
    )

    assert "__interrupt__" in first_result

    second_result = graph.invoke(
        Command(
            resume="Students authenticate using university SSO."
        ),
        config=config,
    )

    assert "__interrupt__" in second_result

    interrupt_data = second_result["__interrupt__"][0].value

    assert (
        "What response-time target should the system meet?"
        in interrupt_data["questions"]
    )

    final_result = graph.invoke(
        Command(
            resume="Normal user actions should complete within 2 seconds."
        ),
        config=config,
    )

    assert final_result["clarification_round"] == 2
    assert final_result["validation_passed"] is True
    assert final_result["validation_issues"] == []


def always_failing_validator(state):
    """Simulate unresolved validation issues."""

    issue = ValidationIssue(
        issue_type=ValidationIssueType.SECURITY,
        severity="high",
        description="Authorization rules remain undefined.",
        clarification_question=(
            "What authorization rules should the system enforce?"
        ),
    )

    return {
        "validation_issues": [issue],
        "validation_passed": False,
        "open_questions": [
            "What authorization rules should the system enforce?"
        ],
    }


def analyzer_ready_immediately(state):
    """Return enough coverage to attempt validation."""

    return {
        "coverage": complete_coverage(),
        "open_questions": [],
    }


def test_max_rounds_stop_failed_validation_loop() -> None:
    graph = build_graph(
        analyzer=analyzer_ready_immediately,
        validator=always_failing_validator,
    )

    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    state["clarification_round"] = 3

    config = {
        "configurable": {
            "thread_id": "max-rounds-thread"
        }
    }

    result = graph.invoke(
        state,
        config=config,
    )

    assert "__interrupt__" not in result
    assert result["ready_for_validation"] is True
    assert result["validation_passed"] is False
    assert len(result["validation_issues"]) == 1