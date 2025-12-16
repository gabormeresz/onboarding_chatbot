from onboarding_agent.core.state import AgentState
from onboarding_agent.models.chat import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


def classify_intent_node(state: AgentState) -> AgentState:
    """
    Classifies the user's query intent into one of several categories.

    Categories:
    - policy_question: Questions about company policies, HR, benefits
    - it_question: IT support, technical issues, equipment
    - critical_issue: Urgent problems requiring immediate escalation
    - ambiguous: Unclear queries needing clarification
    """
    user_query = state["user_query"]

    llm = get_chat_model()

    system_prompt = """You are an intent classifier for an employee onboarding assistant.
Classify the user's query into ONE of these categories:
- policy_question: Questions about HR policies, benefits, onboarding procedures, company guidelines
- it_question: IT support questions, technical troubleshooting, equipment, access issues
- critical_issue: Urgent problems like security incidents, data breaches, system outages requiring immediate escalation
- ambiguous: Unclear or vague queries that need more context

Respond with ONLY the category name, nothing else."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]

    response = llm.invoke(messages)
    content = (
        response.content if isinstance(response.content, str) else str(response.content)
    )
    intent = content.strip().lower()

    # Validate the intent
    valid_intents = ["policy_question", "it_question", "critical_issue", "ambiguous"]
    if intent not in valid_intents:
        intent = "ambiguous"

    state["intent"] = intent
    return state
