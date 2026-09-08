"""Pydantic schemas used by the requirements collection workflow."""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model that rejects unexpected fields."""

    model_config = ConfigDict(extra="forbid")


class RequirementCategory(str, Enum):
    """Requirement areas checked during requirements elicitation."""

    ACTORS = "actors"
    FUNCTIONAL = "functional"
    NON_FUNCTIONAL = "non_functional"
    DATA = "data"
    SECURITY = "security"
    CONSTRAINTS = "constraints"
    DEPENDENCIES = "dependencies"
    ASSUMPTIONS = "assumptions"


class CoverageStatus(str, Enum):
    """How well a requirement category is currently understood."""

    MISSING = "missing"
    PARTIAL = "partial"
    COVERED = "covered"


class Stakeholder(StrictModel):
    """A person or role that interacts with or has an interest in the system."""

    role: str = Field(min_length=1)
    goals: list[str] = Field(default_factory=list)


class Requirement(StrictModel):
    """A requirement collected from the stakeholder conversation."""

    category: RequirementCategory
    statement: str = Field(min_length=1)


class ClarificationQuestion(StrictModel):
    """A question the agent wants the stakeholder to answer."""

    category: RequirementCategory
    question: str = Field(min_length=1)
    rationale: str = Field(min_length=1)


class CoverageAssessment(StrictModel):
    """Assessment of one requirement category."""

    category: RequirementCategory
    status: CoverageStatus
    notes: str = ""


class AnalysisResult(StrictModel):
    """Structured output expected from the requirements-analysis agent."""

    stakeholders: list[Stakeholder] = Field(default_factory=list)
    requirements: list[Requirement] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    coverage: list[CoverageAssessment] = Field(default_factory=list)
    clarification_questions: list[ClarificationQuestion] = Field(default_factory=list)


class ValidationIssueType(str, Enum):
    """Types of issues the validation stage can identify."""

    MISSING = "missing"
    CONTRADICTION = "contradiction"
    AMBIGUOUS = "ambiguous"
    SECURITY = "security"
    ACTOR = "actor"
    TESTABILITY = "testability"
    CONSTRAINT = "constraint"
    DEPENDENCY = "dependency"


class ValidationIssue(StrictModel):
    """A problem found while validating the collected requirements."""

    issue_type: ValidationIssueType
    severity: Literal["low", "medium", "high"]
    description: str = Field(min_length=1)
    clarification_question: str | None = None


class ValidationResult(StrictModel):
    """Structured output expected from the validator."""

    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)


class FunctionalRequirement(StrictModel):
    """Functional requirement in the final requirements specification."""

    id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    acceptance_criteria: list[str] = Field(default_factory=list)


class NonFunctionalRequirement(StrictModel):
    """Non-functional requirement with a measurable quality target."""

    id: str = Field(min_length=1)
    quality_attribute: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    measure: str = Field(min_length=1)


class Epic(StrictModel):
    """High-level capability grouping."""

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)


class UserStory(StrictModel):
    """User story derived from the validated requirements."""

    id: str = Field(min_length=1)
    epic: str = Field(min_length=1)
    actor: str = Field(min_length=1)
    story: str = Field(min_length=1)
    acceptance_criteria: list[str] = Field(default_factory=list)


class FinalSpecification(StrictModel):
    """Final structured requirements artifact."""

    project_summary: str = Field(min_length=1)
    actors: list[Stakeholder] = Field(default_factory=list)
    functional_requirements: list[FunctionalRequirement] = Field(default_factory=list)
    non_functional_requirements: list[NonFunctionalRequirement] = Field(default_factory=list)
    epics: list[Epic] = Field(default_factory=list)
    user_stories: list[UserStory] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    open_assumptions: list[str] = Field(default_factory=list)