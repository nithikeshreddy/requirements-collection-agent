"""Requirements validation node."""

from requirements_agent.llm.provider import get_chat_model
from requirements_agent.prompts.validation import VALIDATION_SYSTEM_PROMPT
from requirements_agent.schemas import ValidationResult
from requirements_agent.state import AgentState


def _format_conversation(state: AgentState) -> str:
    """Format stakeholder conversation for validation."""

    return "\n".join(
        f"{turn['role'].upper()}: {turn['content']}"
        for turn in state["conversation_history"]
    )


def _format_requirements(state: AgentState) -> str:
    """Format collected requirements for validation."""

    if not state["collected_requirements"]:
        return "No requirements have been collected."

    return "\n".join(
        f"- [{requirement.category.value}] {requirement.statement}"
        for requirement in state["collected_requirements"]
    )


def _format_assumptions(state: AgentState) -> str:
    """Format current assumptions."""

    if not state["assumptions"]:
        return "No assumptions recorded."

    return "\n".join(
        f"- {assumption}"
        for assumption in state["assumptions"]
    )


def validate_requirements(state: AgentState) -> dict:
    """Validate collected requirements and return state updates."""

    model = get_chat_model()

    structured_model = model.with_structured_output(
        ValidationResult
    )

    messages = [
        (
            "system",
            VALIDATION_SYSTEM_PROMPT,
        ),
        (
            "human",
            f"""
Project idea:
{state["project_idea"]}

Stakeholder conversation:
{_format_conversation(state)}

Collected requirements:
{_format_requirements(state)}

Current assumptions:
{_format_assumptions(state)}

Validate the requirements.
""".strip(),
        ),
    ]

    result = structured_model.invoke(messages)

    validation_passed = (
        result.passed and not result.issues
    )

    clarification_questions = []

    for issue in result.issues:
        question = issue.clarification_question

        if question:
            clarification_questions.append(question)
        else:
            clarification_questions.append(
                "How should the following validation issue be resolved: "
                f"{issue.description}"
            )

    return {
        "validation_issues": result.issues,
        "validation_passed": validation_passed,
        "open_questions": clarification_questions[:5],
    }