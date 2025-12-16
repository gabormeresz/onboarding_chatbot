from onboarding_agent.core.state import AgentState
from onboarding_agent.tools.ticket_tool import create_ticket_tool
from onboarding_agent.models.chat import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


def escalation_node(state: AgentState) -> AgentState:
    """
    Handles critical issues by creating a support ticket using the ticket tool.
    Uses LLM to extract relevant information from the user query.
    """
    user_query = state["user_query"]

    llm = get_chat_model()

    # Use LLM to extract ticket parameters from the query
    system_prompt = """You are extracting information to create a support ticket.
Based on the user's query, provide:
1. issue_description: Brief description of the issue
2. priority: High (since this is a critical issue)
3. department: IT, HR, Security, or Facilities
4. contact_email: Use "user@company.com" as default

Format your response as:
DESCRIPTION: <description>
PRIORITY: High
DEPARTMENT: <department>
EMAIL: user@company.com"""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]

    response = llm.invoke(messages)
    content = (
        response.content if isinstance(response.content, str) else str(response.content)
    )
    lines = content.strip().split("\n")

    # Parse the response
    issue_description = user_query  # Default to full query
    priority = "High"
    department = "IT"  # Default
    contact_email = "user@company.com"

    for line in lines:
        if line.startswith("DESCRIPTION:"):
            issue_description = line.split("DESCRIPTION:", 1)[1].strip()
        elif line.startswith("DEPARTMENT:"):
            dept = line.split("DEPARTMENT:", 1)[1].strip()
            if dept in ["IT", "HR", "Security", "Facilities"]:
                department = dept
        elif line.startswith("EMAIL:"):
            email = line.split("EMAIL:", 1)[1].strip()
            if email:
                contact_email = email

    # Create the ticket using the tool
    ticket_result = create_ticket_tool.invoke(
        {
            "issue_description": issue_description,
            "priority": priority,
            "department": department,
            "contact_email": contact_email,
        }
    )

    state["ticket_info"] = ticket_result

    # Set the answer based on ticket creation result
    if ticket_result.get("status") == "success":
        state["answer"] = ticket_result.get("message", "Ticket created successfully.")
    else:
        state["answer"] = (
            f"I've escalated your critical issue. {ticket_result.get('message', 'Please contact support directly.')}"
        )

    return state
