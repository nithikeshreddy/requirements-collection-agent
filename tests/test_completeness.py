"""Tests for deterministic completeness rules."""

from requirements_agent.completeness import (
    CORE_CATEGORIES,
    requirements_ready_for_validation,
)
from requirements_agent.schemas import (
    CoverageAssessment,
    CoverageStatus,
    RequirementCategory,
)
from requirements_agent.state import create_initial_state


def make_coverage(
    status: CoverageStatus,
) -> list[CoverageAssessment]:
    return [
        CoverageAssessment(
            category=category,
            status=status,
        )
        for category in CORE_CATEGORIES
    ]


def test_complete_coverage_is_ready() -> None:
    state = create_initial_state("Build a reservation system.")

    state["coverage"] = make_coverage(CoverageStatus.PARTIAL)
    state["open_questions"] = ["One remaining question?"]

    assert requirements_ready_for_validation(state) is True


def test_missing_core_category_is_not_ready() -> None:
    state = create_initial_state("Build a reservation system.")

    state["coverage"] = make_coverage(CoverageStatus.PARTIAL)

    state["coverage"] = [
        assessment
        for assessment in state["coverage"]
        if assessment.category != RequirementCategory.SECURITY
    ]

    assert requirements_ready_for_validation(state) is False


def test_too_many_open_questions_is_not_ready() -> None:
    state = create_initial_state("Build a reservation system.")

    state["coverage"] = make_coverage(CoverageStatus.PARTIAL)

    state["open_questions"] = [
        "Question one?",
        "Question two?",
        "Question three?",
    ]

    assert requirements_ready_for_validation(state) is False


def test_max_rounds_forces_validation_attempt() -> None:
    state = create_initial_state("Build a reservation system.")

    state["coverage"] = []
    state["open_questions"] = ["Still incomplete."]
    state["clarification_round"] = 3

    assert requirements_ready_for_validation(state) is True