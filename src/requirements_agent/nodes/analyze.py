"""Requirements analysis node."""

from requirements_agent.llm.provider import get_chat_model
from requirements_agent.prompts.analysis import ANALYSIS_SYSTEM_PROMPT
from requirements_agent.schemas import AnalysisResult
from requirements_agent.state import AgentState


def _format_conversation(state: AgentState) -> str:
    """Convert conversation history into readable text for the LLM."""

    lines = []

    for turn in state["conversation_history"]:
        role = turn["role"].upper()
        lines.append(f"{role}: {turn['content']}")

    return "\n".join(lines)


def analyze_requirements(state: AgentState) -> dict:
    """Analyze current requirements and return structured state updates."""

    model = get_chat_model()

    structured_model = model.with_structured_output(AnalysisResult)

    conversation = _format_conversation(state)

    messages = [
        (
            "system",
            ANALYSIS_SYSTEM_PROMPT,
        ),
        (
            "human",
            f"""
Project idea:
{state["project_idea"]}

Conversation so far:
{conversation}

Analyze the current requirements information.
""".strip(),
        ),
    ]

    result = structured_model.invoke(messages)

    return {
        "stakeholders": result.stakeholders,
        "collected_requirements": result.requirements,
        "assumptions": result.assumptions,
        "coverage": result.coverage,
        "open_questions": [
            question.question
            for question in result.clarification_questions
        ],
    }