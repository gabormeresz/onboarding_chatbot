import json
import os
import uuid
from langchain_core.tools import tool


@tool
def create_ticket_tool(
    issue_description: str, priority: str, department: str, contact_email: str
) -> dict[str, str]:
    """
    Create a support ticket in the ticketing system.

    Args:
        issue_description (str): Description of the issue.
        priority (str): Priority level of the ticket (e.g., Low, Medium, High).
        department (str): Department to which the ticket should be assigned.
        contact_email (str): Contact email for follow-up.

    Returns:
        dict[str, str]: Confirmation message with ticket ID.
    """
    try:
        # Simulate ticket creation logic
        ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
        ticket_data = {
            "ticket_id": ticket_id,
            "issue_description": issue_description,
            "priority": priority,
            "department": department,
            "contact_email": contact_email,
        }
        os.makedirs(".storage/tickets", exist_ok=True)
        ticket_file = os.path.join(".storage/tickets", f"{ticket_id}.json")
        with open(ticket_file, "w") as f:
            json.dump(ticket_data, f, indent=4)

        confirmation_message = (
            f"Support ticket {ticket_id} created successfully for the {department} department. "
            f"We will contact you at {contact_email} regarding the issue: '{issue_description}'."
        )

        return {
            "status": "success",
            "ticket_id": ticket_id,
            "message": confirmation_message,
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to create ticket: {str(e)}"}
