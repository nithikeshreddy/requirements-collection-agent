"""Run an interactive requirements collection example."""

from uuid import uuid4

from langgraph.types import Command

from requirements_agent.graph import build_graph
from requirements_agent.state import create_initial_state


def main() -> None:
    graph = build_graph()

    state = create_initial_state(
        "Build an application where university students can reserve study rooms."
    )

    config = {
        "configurable": {
            "thread_id": str(uuid4())
        }
    }

    result = graph.invoke(
        state,
        config=config,
    )

    while "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value

        print(
            f"\nClarification Round "
            f"{interrupt_data['round']}"
        )

        for index, question in enumerate(
            interrupt_data["questions"],
            start=1,
        ):
            print(f"{index}. {question}")

        print("\nAnswer the questions in one response.")

        response = input("\nStakeholder: ")

        result = graph.invoke(
            Command(resume=response),
            config=config,
        )

    print("\nRequirements collection finished.")
    print(
        "Ready for validation:",
        result["ready_for_validation"],
    )


if __name__ == "__main__":
    main()