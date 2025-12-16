from typing import TypedDict, Optional


class AgentState(TypedDict):
    user_query: str
    rewritten_query: Optional[str]  # Rewritten query optimized for retrieval
    intent: Optional[str]  # Intent classification result
    route_decision: Optional[str]  # Router decision: "rag", "escalation", or "direct"
    retrieved_docs: list  # Documents from RAG retrieval
    answer: str  # Final answer to return
    needs_escalation: bool  # Flag for whether escalation is needed
    ticket_info: Optional[dict]  # Ticket information if escalated


initial_state: AgentState = {
    "user_query": "",
    "rewritten_query": None,
    "intent": None,
    "route_decision": None,
    "retrieved_docs": [],
    "answer": "",
    "needs_escalation": False,
    "ticket_info": None,
}


def build_initial_state(user_query: str = "") -> AgentState:
    """Build a fresh initial state with the given user query.
    
    Args:
        user_query: The user's question or query (default: empty string)
        
    Returns:
        A new AgentState dictionary with all fields initialized to defaults
    """
    return {
        "user_query": user_query,
        "rewritten_query": None,
        "intent": None,
        "route_decision": None,
        "retrieved_docs": [],
        "answer": "",
        "needs_escalation": False,
        "ticket_info": None,
    }
