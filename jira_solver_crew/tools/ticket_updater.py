"""
TicketUpdaterTool — Sets a ticket's status to 'done', assigns to AI Crew,
and appends to resolution_log.json.
"""

import json
import os
import re
from datetime import datetime
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "..", "tickets.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
RESOLUTION_LOG_PATH = os.path.join(OUTPUT_DIR, "resolution_log.json")


class TicketUpdaterToolSchema(BaseModel):
    ticket_id: str = Field(..., description="The Jira ticket ID, e.g. 'JIRA-101'")
    resolution_branch: str = Field(..., description="The Git branch name, e.g. 'fix/JIRA-101'")


class TicketUpdaterTool(BaseTool):
    name: str = "update_ticket"
    description: str = (
        "Updates a ticket's status to 'done' in tickets.json, assigns it to "
        "'AI Crew', sets the resolution_branch, and appends an entry to "
        "output/resolution_log.json. Pass 'ticket_id' (e.g. 'JIRA-101') and "
        "'resolution_branch' (e.g. 'fix/JIRA-101')."
    )
    args_schema: type[BaseModel] = TicketUpdaterToolSchema

    def _run(self, ticket_id: str, resolution_branch: str, **kwargs) -> str:
        tickets_path = os.path.abspath(TICKETS_PATH)

        # Derive expected fixed filename and verify it exists in output/
        # e.g. JIRA-101 linked to auth/login.py → fixed_login.py
        with open(tickets_path, "r", encoding="utf-8") as f:
            tickets = json.load(f)

        linked_file = None
        for t in tickets:
            if t.get("id") == ticket_id:
                linked_file = t.get("linked_file", "")
                break

        if linked_file:
            base_name = os.path.basename(linked_file)          # e.g. login.py
            fixed_name = f"fixed_{base_name}"                  # e.g. fixed_login.py
            fixed_path = os.path.join(os.path.abspath(OUTPUT_DIR), fixed_name)
            if not os.path.exists(fixed_path):
                return (
                    f"ERROR: Cannot close {ticket_id} — fixed file "
                    f"'output/{fixed_name}' does not exist yet. "
                    f"The code fixer must write the file first using write_code_file."
                )

            with open(fixed_path, "r", encoding="utf-8") as f:
                fixed_code = f.read()

            if not fixed_code.strip() or "def " not in fixed_code:
                return (
                    f"ERROR: Cannot close {ticket_id} — output/{fixed_name} "
                    "is not valid Python source."
                )

            source_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", linked_file))
            if os.path.exists(source_path):
                with open(source_path, "r", encoding="utf-8") as f:
                    source_code = f.read()
                if fixed_code == source_code:
                    return (
                        f"ERROR: Cannot close {ticket_id} — output/{fixed_name} is identical "
                        "to source; no bug fix detected."
                    )

            ticket_desc = ""
            for t in tickets:
                if t.get("id") == ticket_id:
                    ticket_desc = (t.get("description") or "").lower()
                    break

            if "case-sensitive" in ticket_desc and "email" in ticket_desc:
                if "users_db.get(email.lower())" not in fixed_code.lower():
                    return (
                        f"ERROR: Cannot close {ticket_id} — expected case-insensitive email "
                        "lookup fix not found (USERS_DB.get(email.lower()))."
                    )

            if "phone" in ticket_desc and "regex" in ticket_desc:
                has_re_import = "import re" in fixed_code
                has_phone_regex = re.search(r"\\d\{10,15\}", fixed_code) is not None
                has_re_match = "re.match" in fixed_code
                if not (has_re_import and has_phone_regex and has_re_match):
                    return (
                        f"ERROR: Cannot close {ticket_id} — expected phone regex validation "
                        "fix not found (import re + re.match + \\d{10,15})."
                    )

        # Update tickets.json  (reuse already-loaded tickets list)
        updated = False
        for ticket in tickets:
            if ticket.get("id") == ticket_id:
                ticket["status"] = "done"
                ticket["assigned_to"] = "AI Crew"
                ticket["resolution_branch"] = resolution_branch
                updated = True
                break

        if not updated:
            return f"ERROR: Ticket {ticket_id} not found in tickets.json"

        with open(tickets_path, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)

        # Append to resolution log
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        log_entry = {
            "ticket_id": ticket_id,
            "status": "done",
            "assigned_to": "AI Crew",
            "resolution_branch": resolution_branch,
            "resolved_at": datetime.now().isoformat(),
        }

        if os.path.exists(RESOLUTION_LOG_PATH):
            with open(RESOLUTION_LOG_PATH, "r", encoding="utf-8") as f:
                log = json.load(f)
        else:
            log = []

        log.append(log_entry)

        with open(RESOLUTION_LOG_PATH, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2)

        return f"SUCCESS: Ticket {ticket_id} marked as done. Resolution logged."
