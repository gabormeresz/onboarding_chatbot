from onboarding_agent.agent.state import AgentState


def router_node(state: AgentState) -> AgentState:
    """
    Routes the query based on intent classification.

    Routes to:
    - "response_generation" for policy_question, it_question, or ambiguous
    - "escalation" for critical_issue
    """
    intent = state.get("intent", "ambiguous")

    if intent == "critical_issue":
        route_decision = "escalation"
        state["needs_escalation"] = True
    else:
        # policy_question, it_question, or ambiguous go to response generation
        route_decision = "response_generation"
        state["needs_escalation"] = False

    state["route_decision"] = route_decision
    return state
