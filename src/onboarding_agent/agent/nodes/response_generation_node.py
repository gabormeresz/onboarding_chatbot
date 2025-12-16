from onboarding_agent.agent.state import AgentState
from onboarding_agent.models.chat import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


def response_generation_node(state: AgentState) -> AgentState:
    """
    Determines if RAG grounding is needed and generates response accordingly.

    For policy/IT questions: typically needs RAG
    For ambiguous: might need RAG to provide context

    Sets route_decision to "needs_rag" or "direct_answer"
    """
    user_query = state["user_query"]
    intent = state.get("intent", "ambiguous")

    # Policy and IT questions almost always need RAG for grounding
    if intent in ["policy_question", "it_question"]:
        state["route_decision"] = "needs_rag"
        return state

    # For ambiguous queries, decide if we need RAG
    llm = get_chat_model()

    system_prompt = """You are deciding if a query needs to search company documentation.
If the query is asking about company policies, procedures, equipment, or onboarding information, respond: NEEDS_RAG
If the query is too vague or just a greeting, respond: DIRECT

Respond with ONLY "NEEDS_RAG" or "DIRECT", nothing else."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]

    response = llm.invoke(messages)
    content = (
        response.content if isinstance(response.content, str) else str(response.content)
    )
    decision = content.strip().upper()

    if "NEEDS_RAG" in decision:
        state["route_decision"] = "needs_rag"
    else:
        state["route_decision"] = "direct_answer"
        # Generate a simple response for ambiguous/unclear queries
        state["answer"] = (
            "I'm not sure I understand your question. Could you please provide more details about what you need help with? I can assist with onboarding procedures, company policies, IT support, and equipment information."
        )

    return state
