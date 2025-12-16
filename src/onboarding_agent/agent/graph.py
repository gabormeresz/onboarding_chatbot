"""
Main LangGraph implementation for the onboarding agent.

Flow:
1. User Query -> Intent Classification
2. Intent Classification -> Decision Router
3. Decision Router:
   - Policy/IT/Ambiguous -> Response Generation -> (RAG if needed) -> Final Response
   - Critical Issue -> Escalation Tool -> Final Response
"""

from langgraph.graph import StateGraph, START, END
from onboarding_agent.agent.state import AgentState
from onboarding_agent.agent.nodes.classify_intent_node import classify_intent_node
from onboarding_agent.agent.nodes.router_node import router_node
from onboarding_agent.agent.nodes.response_generation_node import (
    response_generation_node,
)
from onboarding_agent.agent.nodes.rag_call_node import rag_call_node
from onboarding_agent.agent.nodes.escalation_node import escalation_node
from onboarding_agent.agent.nodes.compose_final_answer_node import (
    compose_final_answer_node,
)


def route_after_router(state: AgentState) -> str:
    """
    Conditional edge function that routes after the decision router.
    Returns the next node name based on route_decision.
    """
    route_decision = state.get("route_decision", "response_generation")

    if route_decision == "escalation":
        return "escalation"
    else:
        return "response_generation"


def route_after_response_gen(state: AgentState) -> str:
    """
    Conditional edge function after response generation.
    Routes to RAG if needed, otherwise to final answer.
    """
    route_decision = state.get("route_decision", "direct_answer")

    if route_decision == "needs_rag":
        return "rag_call"
    else:
        return "final_answer"


def build_graph():
    """
    Builds and compiles the main agent graph.
    """
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("classify_intent", classify_intent_node)
    graph.add_node("router", router_node)
    graph.add_node("response_generation", response_generation_node)
    graph.add_node("rag_call", rag_call_node)
    graph.add_node("escalation", escalation_node)
    graph.add_node("final_answer", compose_final_answer_node)

    # Define edges
    # Start -> Intent Classification
    graph.add_edge(START, "classify_intent")

    # Intent Classification -> Router
    graph.add_edge("classify_intent", "router")

    # Router -> (Response Generation OR Escalation) - conditional
    graph.add_conditional_edges(
        "router",
        route_after_router,
        {"response_generation": "response_generation", "escalation": "escalation"},
    )

    # Response Generation -> (RAG Call OR Final Answer) - conditional
    graph.add_conditional_edges(
        "response_generation",
        route_after_response_gen,
        {"rag_call": "rag_call", "final_answer": "final_answer"},
    )

    # RAG Call -> Final Answer
    graph.add_edge("rag_call", "final_answer")

    # Escalation -> Final Answer
    graph.add_edge("escalation", "final_answer")

    # Final Answer -> END
    graph.add_edge("final_answer", END)

    return graph.compile()
