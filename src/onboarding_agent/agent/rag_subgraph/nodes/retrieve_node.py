from onboarding_agent.agent.rag_subgraph.vectorstore import get_vectorstore
from onboarding_agent.core.state import AgentState


def retrieve_node(state: AgentState) -> dict:
    """Retrieve relevant documents from Chroma vectorstore."""
    vectordb = get_vectorstore()

    # Use rewritten query if available, otherwise use original
    query = state.get("rewritten_query") or state["user_query"]
    results = vectordb.similarity_search_with_score(query, k=5)

    docs = []
    for doc, score in results:
        docs.append(
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
        )

    return {"retrieved_docs": docs}
