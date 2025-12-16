from onboarding_agent.rag.subgraph.graph import build_graph as build_rag_graph
from onboarding_agent.agent.state import AgentState


def rag_call_node(state: AgentState) -> dict:
    """
    Invokes the RAG subgraph to retrieve documents and generate an answer.
    Returns the updated state from the subgraph to propagate changes to parent graph.
    """
    rag_graph = build_rag_graph()

    # Invoke the RAG subgraph and return its state updates
    result = rag_graph.invoke(state)

    return result
