import time
from onboarding_agent.rag.vectorstore import get_vectorstore
from onboarding_agent.agent.state import AgentState


def retrieve_node(state: AgentState, max_retries: int = 3) -> dict:
    """Retrieve relevant documents from Chroma vectorstore.

    Includes retry logic to handle transient Ollama embedding errors (e.g., NaN values).
    """
    vectordb = get_vectorstore()

    # Use rewritten query if available, otherwise use original
    query = state.get("rewritten_query") or state["user_query"]

    # Retry logic for transient Ollama errors
    results = []
    last_error = None
    for attempt in range(max_retries):
        try:
            results = vectordb.similarity_search_with_score(query, k=5)
            break
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = (2**attempt) + (0.1 * attempt)  # Exponential backoff
                print(
                    f"Embedding error (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time:.1f}s..."
                )
                time.sleep(wait_time)
            else:
                raise RuntimeError(
                    f"Failed to retrieve docs after {max_retries} attempts: {last_error}"
                ) from e

    docs = []
    for doc, score in results:
        docs.append(
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
        )

    return {"retrieved_docs": docs}
