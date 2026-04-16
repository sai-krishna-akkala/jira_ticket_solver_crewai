"""
TicketReaderTool — Reads tickets.json, filters open tickets, sorts by priority,
and returns the highest-priority open ticket.
"""

import json
import os
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "tickets.json")


class TicketReaderToolSchema(BaseModel):
    pass


class TicketReaderTool(BaseTool):
    name: str = "read_tickets"
    description: str = (
        "Reads tickets.json, filters for open tickets, sorts by priority "
        "(P0 highest), and returns the top open ticket as a JSON string. "
        "No arguments required."
    )
    args_schema: type[BaseModel] = TicketReaderToolSchema

    def _run(self, **kwargs) -> str:
        tickets_path = os.path.abspath(TICKETS_PATH)
        if not os.path.exists(tickets_path):
            return "ERROR: tickets.json not found."

        with open(tickets_path, "r", encoding="utf-8") as f:
            tickets = json.load(f)

        open_tickets = [t for t in tickets if t.get("status") == "open"]

        if not open_tickets:
            return "NO_OPEN_TICKETS"

        open_tickets.sort(key=lambda t: PRIORITY_ORDER.get(t.get("priority", "P3"), 99))

        top_ticket = open_tickets[0]
        return json.dumps(top_ticket, indent=2)
