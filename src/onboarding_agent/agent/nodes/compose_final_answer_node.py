from onboarding_agent.agent.state import AgentState


def compose_final_answer_node(state: AgentState) -> AgentState:
    """
    Ensures the final answer is properly formatted and available in the state.
    This is mostly a pass-through since answers are set by previous nodes.
    """
    # The answer should already be set by either:
    # - RAG call node
    # - Response generation node (for direct answers)
    # - Escalation node (for critical issues)

    # If somehow no answer was generated, provide a fallback
    if not state.get("answer"):
        state["answer"] = (
            "I apologize, but I couldn't process your request. Please try rephrasing your question or contact support directly."
        )

    return state
