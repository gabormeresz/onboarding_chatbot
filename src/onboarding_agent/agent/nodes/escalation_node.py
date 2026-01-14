from onboarding_agent.agent.state import AgentState
from onboarding_agent.tools.ticket_tool import create_ticket_tool
from onboarding_agent.models.chat import get_chat_model
from langchain_core.messages import SystemMessage, HumanMessage


def escalation_node(state: AgentState) -> AgentState:
    """
    Handles critical issues by creating a support ticket using the ticket tool.
    Uses LLM with bound tool to automatically create the ticket.
    """
    user_query = state["user_query"]

    # Get chat model with tool binding
    llm_with_tool = get_chat_model(tools=[create_ticket_tool])

    # System prompt to guide the LLM to use the tool
    system_prompt = """You are a support assistant handling a critical issue that requires escalation.
You have access to a create_ticket tool. Use it to create a support ticket based on the user's query.

For the ticket parameters:
- issue_description: Extract or summarize the key issue from the user's query
- priority: Always set to "High" for critical issues
- department: Choose from IT, HR, Security, or Facilities based on the issue type
- contact_email: Use "user@company.com" as the default contact

Call the create_ticket tool with appropriate parameters."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_query)]

    # Invoke LLM with tool
    response = llm_with_tool.invoke(messages)

    # Check if the LLM called the tool
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        # Execute the tool call
        ticket_result = create_ticket_tool.invoke(tool_call["args"])
        state["ticket_info"] = ticket_result

        # Set the answer based on ticket creation result
        if ticket_result.get("status") == "success":
            state["answer"] = ticket_result.get(
                "message", "Ticket created successfully."
            )
        else:
            state["answer"] = (
                f"I've escalated your critical issue. {ticket_result.get('message', 'Please contact support directly.')}"
            )
    else:
        # Fallback if tool wasn't called
        state["answer"] = (
            "I've escalated your critical issue to support. Someone will contact you shortly."
        )
        state["ticket_info"] = {
            "status": "pending",
            "message": "Manual escalation required",
        }

    return state
