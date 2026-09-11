"""Deterministic requirements completeness checks."""

from requirements_agent.schemas import CoverageStatus, RequirementCategory
from requirements_agent.state import AgentState

CORE_CATEGORIES = (
    RequirementCategory.ACTORS,
    RequirementCategory.FUNCTIONAL,
    RequirementCategory.NON_FUNCTIONAL,
    RequirementCategory.DATA,
    RequirementCategory.SECURITY,
    RequirementCategory.CONSTRAINTS,
    RequirementCategory.DEPENDENCIES,
)


def requirements_ready_for_validation(state: AgentState) -> bool:
    """Determine whether requirements are ready to attempt validation.

    This is deliberately deterministic. The LLM supplies coverage assessments,
    but Python decides whether the workflow can proceed to validation.
    """

    if state["clarification_round"] >= state["max_clarification_rounds"]:
        return True

    coverage_by_category = {
        assessment.category: assessment.status
        for assessment in state["coverage"]
    }

    for category in CORE_CATEGORIES:
        status = coverage_by_category.get(
            category,
            CoverageStatus.MISSING,
        )

        if status == CoverageStatus.MISSING:
            return False

    return len(state["open_questions"]) <= 2

    return True