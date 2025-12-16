from onboarding_agent.agent.state import AgentState
from onboarding_agent.models.chat import get_chat_model


def rewrite_for_retrieval_node(state: AgentState) -> dict:
    """Rewrite the user query to optimize it for retrieval."""
    llm = get_chat_model()

    original_query = state["user_query"]

    rewrite_prompt = f"""Given the following user question about employee onboarding, IT policies, HR information, or workplace procedures, 
rewrite it to be more effective for semantic search retrieval. 
Make it more specific, add relevant keywords, and structure it as a clear information need.

Original question: {original_query}

Rewritten query (respond with ONLY the rewritten query, no explanations):"""

    response = llm.invoke(rewrite_prompt)
    rewritten_query = response.content

    # Store the rewritten query in a separate field
    return {"rewritten_query": rewritten_query}
