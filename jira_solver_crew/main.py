"""
main.py — Entry point for the Jira Solver Crew.
Loops until all open tickets in tickets.json are resolved.
"""

import json
import os
import re

from crew import build_crew

TICKETS_PATH = os.path.join(os.path.dirname(__file__), "tickets.json")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
MAX_ATTEMPTS_PER_TICKET = 2


def load_tickets() -> list[dict]:
    with open(TICKETS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_tickets(tickets: list[dict]) -> None:
    with open(TICKETS_PATH, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)


def count_open_tickets() -> int:
    """Return the number of open tickets in tickets.json."""
    tickets = load_tickets()
    return sum(1 for t in tickets if t.get("status") == "open")


def get_next_open_ticket(exclude_ids: set[str] | None = None) -> dict | None:
    """Return the highest-priority open ticket, excluding any IDs in exclude_ids."""
    exclude_ids = exclude_ids or set()
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    tickets = load_tickets()
    open_tickets = [
        t
        for t in tickets
        if t.get("status") == "open" and t.get("id") not in exclude_ids
    ]
    open_tickets.sort(key=lambda t: priority_order.get(t.get("priority", "P3"), 99))
    return open_tickets[0] if open_tickets else None


def expected_fixed_filename(ticket: dict) -> str:
    linked_file = ticket.get("linked_file", "")
    base_name = os.path.basename(linked_file)
    if not base_name:
        return ""
    return f"fixed_{base_name}"


def validate_ticket_completion(ticket_id: str) -> tuple[bool, str]:
    """Validate that ticket is done and expected output artifacts exist."""
    tickets = load_tickets()
    ticket = next((t for t in tickets if t.get("id") == ticket_id), None)
    if not ticket:
        return False, f"Ticket {ticket_id} not found"

    if ticket.get("status") != "done":
        return False, f"Ticket {ticket_id} status is not done"

    fixed_name = expected_fixed_filename(ticket)
    if not fixed_name:
        return False, f"Ticket {ticket_id} has invalid linked_file"

    fixed_path = os.path.join(OUTPUT_DIR, fixed_name)
    if not os.path.exists(fixed_path):
        return False, f"Missing required artifact: output/{fixed_name}"

    source_path = os.path.join(os.path.dirname(__file__), ticket.get("linked_file", ""))
    try:
        with open(fixed_path, "r", encoding="utf-8") as f:
            fixed_code = f.read()
    except Exception as error:
        return False, f"Could not read output/{fixed_name}: {error}"

    if not fixed_code.strip():
        return False, f"output/{fixed_name} is empty"

    if "def " not in fixed_code:
        return False, f"output/{fixed_name} does not look like valid source code"

    if os.path.exists(source_path):
        with open(source_path, "r", encoding="utf-8") as f:
            source_code = f.read()
        if fixed_code == source_code:
            return False, f"output/{fixed_name} is identical to source (no fix applied)"

    description = (ticket.get("description") or "").lower()
    linked_file = (ticket.get("linked_file") or "").lower()

    if "case-sensitive" in description and "email" in description:
        has_lower_lookup = "users_db.get(email.lower())" in fixed_code.lower()
        if not has_lower_lookup:
            return False, (
                f"output/{fixed_name} missing expected case-insensitive email lookup "
                "(USERS_DB.get(email.lower()))"
            )

    if "phone" in description and "regex" in description:
        has_re_import = "import re" in fixed_code
        has_phone_regex = re.search(r"\\d\{10,15\}", fixed_code) is not None
        has_re_match = "re.match" in fixed_code
        if not (has_re_import and has_phone_regex and has_re_match):
            return False, (
                f"output/{fixed_name} missing expected phone regex validation "
                "(import re + re.match + \\d{10,15})"
            )

    return True, f"Validated output/{fixed_name}"


def reopen_ticket(ticket_id: str) -> None:
    """Reset a ticket back to open when a run fails validation."""
    tickets = load_tickets()
    for ticket in tickets:
        if ticket.get("id") == ticket_id:
            ticket["status"] = "open"
            ticket["assigned_to"] = None
            ticket["resolution_branch"] = None
            break
    save_tickets(tickets)


def get_next_ticket_summary() -> str:
    """Return a short summary of the next ticket to process."""
    ticket = get_next_open_ticket()
    if ticket:
        t = ticket
        return f"{t['id']} — {t['title']}"
    return "None"


def main():
    print("=" * 60)
    print("  JIRA SOLVER CREW — Autonomous Bug Fix Pipeline")
    print("  Runs until ALL open tickets are resolved")
    print("=" * 60)
    print()
    print("Pipeline: Intake → Analyze → Navigate → Fix → PR → Close")
    print()

    iteration = 0
    failed_ticket_ids: set[str] = set()

    while True:
        open_count = count_open_tickets()
        if open_count == 0:
            break

        ticket = get_next_open_ticket(exclude_ids=failed_ticket_ids)
        if ticket is None:
            print()
            print("⚠️ No eligible open tickets remain (all remaining tickets failed retries).")
            break

        iteration += 1
        next_ticket = f"{ticket['id']} — {ticket['title']}"

        print("-" * 60)
        print(f"  🔄 ITERATION {iteration}  |  {open_count} open ticket(s) remaining")
        print(f"  Next up: {next_ticket}")
        print("-" * 60)
        print()

        ticket_id = ticket["id"]
        succeeded = False
        for attempt in range(1, MAX_ATTEMPTS_PER_TICKET + 1):
            if attempt > 1:
                print(f"  ↻ Retry {attempt}/{MAX_ATTEMPTS_PER_TICKET} for {ticket_id}")

            try:
                crew = build_crew()
                crew.kickoff(
                    inputs={
                        "ticket_id": ticket_id,
                        "ticket_title": ticket.get("title", ""),
                        "ticket_description": ticket.get("description", ""),
                        "linked_file": ticket.get("linked_file", ""),
                    }
                )
            except Exception as error:
                print(f"  ✗ Crew execution failed for {ticket_id}: {error}")

            valid, message = validate_ticket_completion(ticket_id)
            if valid:
                succeeded = True
                print(f"  ✓ Validation passed: {message}")
                break

            print(f"  ✗ Validation failed: {message}")
            reopen_ticket(ticket_id)

        if not succeeded:
            failed_ticket_ids.add(ticket_id)
            print(f"  ⚠️ Marked {ticket_id} as failed after {MAX_ATTEMPTS_PER_TICKET} attempts")

        print()
        print(f"  ✓ Iteration {iteration} complete")
        print()

    if count_open_tickets() == 0:
        print("=" * 60)
        print("  ✅ ALL TICKETS RESOLVED — No open tickets remaining!")
        print("=" * 60)
    else:
        print("=" * 60)
        print("  ⚠️ RUN FINISHED WITH UNRESOLVED TICKETS")
        print("  Review logs and retry after fixing prompt/tool issues.")
        print("=" * 60)


if __name__ == "__main__":
    main()
