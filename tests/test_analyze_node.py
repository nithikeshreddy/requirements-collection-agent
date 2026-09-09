"""Tests for the requirements analysis node."""

from unittest.mock import MagicMock, patch

from requirements_agent.nodes.analyze import analyze_requirements
from requirements_agent.schemas import (
    AnalysisResult,
    ClarificationQuestion,
    CoverageAssessment,
    CoverageStatus,
    Requirement,
    RequirementCategory,
    Stakeholder,
)
from requirements_agent.state import create_initial_state


def test_analyze_requirements_updates_state() -> None:
    state = create_initial_state(
        "Build an application where university students can reserve study rooms."
    )

    fake_result = AnalysisResult(
        stakeholders=[
            Stakeholder(
                role="university student",
                goals=["Reserve study rooms"],
            )
        ],
        requirements=[
            Requirement(
                category=RequirementCategory.FUNCTIONAL,
                statement="Students can reserve study rooms.",
            )
        ],
        assumptions=[],
        coverage=[
            CoverageAssessment(
                category=RequirementCategory.FUNCTIONAL,
                status=CoverageStatus.PARTIAL,
                notes="Reservation capability is known but rules are unclear.",
            )
        ],
        clarification_questions=[
            ClarificationQuestion(
                category=RequirementCategory.SECURITY,
                question="How should students authenticate?",
                rationale="Authentication requirements are not yet defined.",
            )
        ],
    )

    fake_structured_model = MagicMock()
    fake_structured_model.invoke.return_value = fake_result

    fake_model = MagicMock()
    fake_model.with_structured_output.return_value = fake_structured_model

    with patch(
        "requirements_agent.nodes.analyze.get_chat_model",
        return_value=fake_model,
    ):
        updates = analyze_requirements(state)

    assert updates["stakeholders"][0].role == "university student"
    assert len(updates["collected_requirements"]) == 1
    assert updates["open_questions"] == [
        "How should students authenticate?"
    ]