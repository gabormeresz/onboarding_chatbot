from onboarding_agent.agent.state import AgentState
from onboarding_agent.models.chat import get_chat_model
from langchain_core.prompts import ChatPromptTemplate


def answering_node(state: AgentState) -> dict:
    """Generate answer using LLM with retrieved context."""
    llm = get_chat_model()

    retrieved_docs = state.get("retrieved_docs", [])
    user_query = state["user_query"]

    if retrieved_docs:
        # Build context from retrieved documents
        context_parts = []
        for i, doc_info in enumerate(retrieved_docs, 1):
            source = doc_info.get("metadata", {}).get("source", "unknown")
            content = doc_info["content"]
            context_parts.append(f"[Document {i} - {source}]\n{content}")

        context = "\n\n".join(context_parts)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful onboarding assistant. Answer the user's question based on the provided context documents. If the context doesn't contain relevant information, say so politely.",
                ),
                ("user", "Context:\n{context}\n\nQuestion: {question}"),
            ]
        )

        # print("Prompting LLM with context:\n")
        # print(context)
        # print("\n" + "-" * 80 + "\n")

        chain = prompt | llm
        result = chain.invoke({"context": context, "question": user_query})
        resp = result.content
    else:
        # No documents retrieved, return with an error message
        resp = (
            "I'm sorry, I couldn't find relevant information to answer your question."
        )

    return {"answer": resp}
