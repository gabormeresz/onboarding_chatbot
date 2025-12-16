from langgraph.graph import StateGraph, START, END

from onboarding_agent.core.state import AgentState
from onboarding_agent.agent.rag_subgraph.nodes.retrieve_node import retrieve_node
from onboarding_agent.agent.rag_subgraph.nodes.answering_node import answering_node
from onboarding_agent.agent.rag_subgraph.nodes.rewrite_for_retrieval_node import (
    rewrite_for_retrieval_node,
)
from onboarding_agent.core.state import build_initial_state


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("rewrite_query", rewrite_for_retrieval_node)
    g.add_node("retrieve_docs", retrieve_node)
    g.add_node("generate_answer", answering_node)
    g.add_edge(START, "rewrite_query")
    g.add_edge("rewrite_query", "retrieve_docs")
    g.add_edge("retrieve_docs", "generate_answer")
    g.add_edge("generate_answer", END)
    return g.compile()


if __name__ == "__main__":
    graph = build_graph()
    initial_state = build_initial_state("What should I do on my first day")
    out = graph.invoke(initial_state)

    print("\nOriginal query:", out["user_query"])
    print("Rewritten query:", out["rewritten_query"])
    print("\nAnswer:", out["answer"])
