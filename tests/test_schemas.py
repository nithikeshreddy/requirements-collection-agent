"""Tests for Pydantic requirement schemas."""

import pytest
from pydantic import ValidationError

from requirements_agent.schemas import (
    ClarificationQuestion,
    FinalSpecification,
    Requirement,
    RequirementCategory,
)


def test_requirement_schema() -> None:
    requirement = Requirement(
        category=RequirementCategory.FUNCTIONAL,
        statement="Students can reserve an available study room.",
    )

    assert requirement.category == RequirementCategory.FUNCTIONAL


def test_empty_clarification_question_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ClarificationQuestion(
            category=RequirementCategory.SECURITY,
            question="",
            rationale="Authentication requirements are unknown.",
        )


def test_unexpected_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Requirement.model_validate(
            {
                "category": "functional",
                "statement": "Students can reserve rooms.",
                "unexpected_field": "should fail",
            }
        )


def test_final_specification_defaults() -> None:
    specification = FinalSpecification(
        project_summary="Study room reservation application."
    )

    assert specification.functional_requirements == []
    assert specification.user_stories == []