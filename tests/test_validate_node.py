"""Tests for the requirements validation node."""

from unittest.mock import MagicMock, patch

from requirements_agent.nodes.validate import validate_requirements
from requirements_agent.schemas import (
    ValidationIssue,
    ValidationIssueType,
    ValidationResult,
)
from requirements_agent.state import create_initial_state


def test_validator_passes_when_no_issues_exist() -> None:
    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    fake_result = ValidationResult(
        passed=True,
        issues=[],
    )

    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = fake_result

    fake_model = MagicMock()
    fake_model.with_structured_output.return_value = fake_structured_model

    with patch(
        "requirements_agent.nodes.validate.get_chat_model",
        return_value=fake_model,
    ):
        updates = validate_requirements(state)

    assert updates["validation_passed"] is True
    assert updates["validation_issues"] == []
    assert updates["open_questions"] == []


def test_validator_fails_when_issue_exists() -> None:
    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    issue = ValidationIssue(
        issue_type=ValidationIssueType.TESTABILITY,
        severity="medium",
        description=(
            "The requirement 'the application should be fast' "
            "does not define a measurable response time."
        ),
        clarification_question=(
            "What response-time target should the application meet?"
        ),
    )

    fake_result = ValidationResult(
        passed=False,
        issues=[issue],
    )

    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = fake_result

    fake_model = MagicMock()
    fake_model.with_structured_output.return_value = fake_structured_model

    with patch(
        "requirements_agent.nodes.validate.get_chat_model",
        return_value=fake_model,
    ):
        updates = validate_requirements(state)

    assert updates["validation_passed"] is False
    assert updates["validation_issues"] == [issue]
    assert updates["open_questions"] == [
        "What response-time target should the application meet?"
    ]


def test_validator_does_not_trust_passed_when_issues_exist() -> None:
    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    issue = ValidationIssue(
        issue_type=ValidationIssueType.SECURITY,
        severity="high",
        description="Administrator authorization rules are undefined.",
        clarification_question=(
            "What permissions should administrators have?"
        ),
    )

    fake_result = ValidationResult(
        passed=True,
        issues=[issue],
    )

    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = fake_result

    fake_model = MagicMock()
    fake_model.with_structured_output.return_value = fake_structured_model

    with patch(
        "requirements_agent.nodes.validate.get_chat_model",
        return_value=fake_model,
    ):
        updates = validate_requirements(state)

    assert updates["validation_passed"] is False
    assert updates["validation_issues"] == [issue]


def test_validator_creates_fallback_question() -> None:
    state = create_initial_state(
        "Build an application where students can reserve study rooms."
    )

    issue = ValidationIssue(
        issue_type=ValidationIssueType.AMBIGUOUS,
        severity="medium",
        description="The reservation policy is ambiguous.",
        clarification_question=None,
    )

    fake_result = ValidationResult(
        passed=False,
        issues=[issue],
    )

    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = fake_result

    fake_model = MagicMock()
    fake_model.with_structured_output.return_value = fake_structured_model

    with patch(
        "requirements_agent.nodes.validate.get_chat_model",
        return_value=fake_model,
    ):
        updates = validate_requirements(state)

    assert updates["validation_passed"] is False
    assert len(updates["open_questions"]) == 1
    assert "reservation policy is ambiguous" in (
        updates["open_questions"][0]
    )