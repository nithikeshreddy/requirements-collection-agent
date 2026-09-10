"""Human-in-the-loop interaction helpers."""

from requirements_agent.state import AgentState


def record_clarification_response(
    state: AgentState,
    response: str,
) -> AgentState:
    """Record clarification questions and the stakeholder's response."""

    cleaned_response = response.strip() # removing white spaces ( response is agent replied)

    if not cleaned_response:
        raise ValueError("Clarification response cannot be empty.")

    if not state["open_questions"]:
        raise ValueError("There are no open clarification questions.")

    formatted_questions = "\n".join(
        f"{index}. {question}"
        for index, question in enumerate(state["open_questions"], start=1)
    )

    updated_state = state.copy()

    updated_state["conversation_history"] = [
        *state["conversation_history"],
        {
            "role": "agent",
            "content": f"Clarification questions:\n{formatted_questions}",
        },
        {
            "role": "stakeholder",
            "content": cleaned_response,
        },
    ]

    updated_state["clarification_round"] = (
        state["clarification_round"] + 1
    )

    return updated_state




