"""
crew.py — Defines 6 AI Agents, 6 Tasks, and the Sequential Crew.

Pipeline: Ticket Intake → Technical Analysis → Code Navigation →
          Code Fix → PR Creation → Ticket Close
"""

from crewai import Agent, Task, Crew, Process

from config.llm_config import get_llm
from tools.ticket_reader import TicketReaderTool
from tools.code_reader import CodeReaderTool
from tools.code_writer import CodeWriterTool
from tools.git_tool import GitTool
from tools.ticket_updater import TicketUpdaterTool

# ── LLM instances ──────────────────────────────────────────
llm = get_llm(temperature=0.7)
llm_precise = get_llm(temperature=0.1)

# ── Tool instances ─────────────────────────────────────────
ticket_reader_tool = TicketReaderTool()
code_reader_tool = CodeReaderTool()
code_writer_tool = CodeWriterTool()
git_tool = GitTool()
ticket_updater_tool = TicketUpdaterTool()


# ══════════════════════════════════════════════════════════════
#  AGENTS
# ══════════════════════════════════════════════════════════════

ticket_intake_agent = Agent(
    role="Ticket Intake Specialist",
    goal=(
        "Read the Jira ticket board (tickets.json), filter for open tickets, "
        "sort by priority (P0 highest), and return the single highest-priority "
        "open ticket."
    ),
    backstory=(
        "You are the team's triage specialist. Every morning you scan the "
        "ticket board and surface the most critical unresolved bug so the "
        "engineering crew can tackle it first."
    ),
    tools=[ticket_reader_tool],
    llm=llm,
    max_iter=2,
    verbose=True,
)

technical_analyst_agent = Agent(
    role="Technical Ticket Analyst",
    goal=(
        "Convert the raw Jira ticket description into a precise, actionable "
        "technical specification that a code fixer can follow."
    ),
    backstory=(
        "You are a senior engineer who translates vague bug reports into "
        "crystal-clear technical specs: root cause hypothesis, affected "
        "component, and exact expected-vs-actual behavior."
    ),
    llm=llm,
    max_iter=2,
    verbose=True,
)

codebase_navigator_agent = Agent(
    role="Codebase Navigator",
    goal=(
        "Read the linked source file, find the exact buggy function and "
        "line numbers, and explain what is wrong."
    ),
    backstory=(
        "You are a code archaeologist who can dive into any codebase, "
        "read source files, and pinpoint the exact lines causing a bug."
    ),
    tools=[code_reader_tool],
    llm=llm,
    max_iter=2,
    verbose=True,
)

code_fixer_agent = Agent(
    role="Autonomous Code Fixer",
    goal=(
        "Read the buggy source file, identify the exact buggy lines, "
        "MODIFY those lines to fix the bug, then save the COMPLETE "
        "corrected file to output/. The fixed file MUST be different "
        "from the original — you must actually change the buggy code."
    ),
    backstory=(
        "You are a meticulous developer who writes minimal, surgical fixes. "
        "You ALWAYS modify the buggy lines — never copy code unchanged. "
        "You read the original, identify root cause from ticket + analysis, "
        "apply the smallest correct change, and save the whole file with "
        "the fix applied."
    ),
    tools=[code_reader_tool, code_writer_tool],
    llm=llm_precise,
    max_iter=3,
    verbose=True,
)

pr_creator_agent = Agent(
    role="PR Creator",
    goal=(
        "Create a Git branch named 'fix/<ticket_id>', commit the fixed "
        "file, and write a PR summary markdown."
    ),
    backstory=(
        "You are the team's release engineer. After every fix, you create "
        "a clean feature branch, commit the change, and draft a pull request "
        "summary so reviewers know exactly what changed and why."
    ),
    tools=[git_tool],
    llm=llm,
    max_iter=2,
    verbose=True,
)

ticket_closer_agent = Agent(
    role="Ticket Closer",
    goal=(
        "Mark the ticket as 'done' in tickets.json, assign it to 'AI Crew', "
        "and log the resolution to output/resolution_log.json."
    ),
    backstory=(
        "You are the operations lead who ensures every resolved ticket is "
        "properly closed, assigned, and logged for audit purposes."
    ),
    tools=[ticket_updater_tool],
    llm=llm,
    max_iter=2,
    verbose=True,
)


# ══════════════════════════════════════════════════════════════
#  TASKS
# ══════════════════════════════════════════════════════════════

task_intake = Task(
    description=(
        "STEP 1: Call the read_tickets tool (no arguments needed). "
        "It will return the highest-priority open ticket as JSON. "
        "Return that JSON exactly as your output — do not modify it."
    ),
    expected_output=(
        "The raw JSON object of the highest-priority open ticket, e.g.:\n"
        '{"id": "JIRA-101", "priority": "P0", "status": "open", '
        '"title": "...", "description": "...", "linked_file": "project_codebase/auth/login.py"}'
    ),
    agent=ticket_intake_agent,
)

task_analyze = Task(
    description=(
        "STEP 2: From the ticket provided by the previous step, produce a "
        "technical spec. Extract: ticket_id, the linked_file path, "
        "root cause hypothesis, expected behavior, and actual (buggy) behavior. "
        "Do NOT use any tools — just analyze the ticket text."
    ),
    expected_output=(
        "A structured spec with ticket_id, linked_file, root_cause, "
        "expected_behavior, actual_behavior."
    ),
    agent=technical_analyst_agent,
    context=[],  # will be set below
)

task_navigate = Task(
    description=(
        "STEP 3: Call the read_code_file tool with the file_path from the "
        "ticket's linked_file field (e.g. file_path='project_codebase/auth/login.py'). "
        "Read the file content, then identify the exact buggy function name "
        "and line numbers. Explain what is wrong."
    ),
    expected_output=(
        "The file content with line numbers, the buggy function name, "
        "the exact line numbers, and what the code does wrong."
    ),
    agent=codebase_navigator_agent,
    context=[],  # will be set below
)

task_fix = Task(
    description=(
        "STEP 4: You MUST do these two things:\n"
        "1) First, call read_code_file with the linked_file path to read the buggy source.\n"
        "2) Then FIX the buggy lines based on the current ticket context.\n"
        "   - Use ticket inputs: ticket_id={ticket_id}, linked_file={linked_file}\n"
        "   - Apply a minimal root-cause fix for this specific bug\n"
        "   - Preserve unrelated behavior and function signatures\n"
        "3) Call write_code_file with TWO arguments:\n"
        "   - filename: 'fixed_<name>.py' (e.g. 'fixed_login.py' for auth/login.py, "
        "     or 'fixed_signup.py' for forms/signup.py)\n"
        "   - code: the COMPLETE corrected Python source code with the bug FIXED\n\n"
        "IMPORTANT: The code you pass to write_code_file MUST have the buggy lines "
        "actually changed. If the original has `USERS_DB.get(email)`, your output MUST "
        "have `USERS_DB.get(email.lower())` — not the same line unchanged.\n"
        "You MUST call write_code_file — do not just print the code."
    ),
    expected_output=(
        "The tool output confirming the file was written, e.g. "
        "'SUCCESS: Wrote 450 bytes to output/fixed_login.py', "
        "plus a brief summary of exactly which line was changed and how."
    ),
    agent=code_fixer_agent,
    context=[],  # will be set below
)

task_pr = Task(
    description=(
        "STEP 5: Call the git_commit tool with exactly these arguments:\n"
        "  - ticket_id: the Jira ID from input {ticket_id}\n"
        "  - filename: the fixed filename (e.g. 'fixed_login.py')\n"
        "  - summary: a one-line description of the fix\n"
        "This creates a Git branch and writes pr_summary.md to output/."
    ),
    expected_output=(
        "Confirmation that the branch was created (or simulated) and "
        "pr_summary.md was written."
    ),
    agent=pr_creator_agent,
    context=[],  # will be set below
)

task_close = Task(
    description=(
        "STEP 6: Call the update_ticket tool with exactly these arguments:\n"
        "  - ticket_id: the Jira ID from input {ticket_id}\n"
        "  - resolution_branch: 'fix/<ticket_id>' (e.g. 'fix/{ticket_id}')\n"
        "This marks the ticket as done and logs the resolution."
    ),
    expected_output=(
        "Confirmation that the ticket is marked done and resolution logged."
    ),
    agent=ticket_closer_agent,
    context=[],  # will be set below
)

# ── Wire up task context so each step receives previous outputs ──
task_analyze.context = [task_intake]
task_navigate.context = [task_intake, task_analyze]
task_fix.context = [task_intake, task_analyze, task_navigate]
task_pr.context = [task_intake, task_fix]
task_close.context = [task_intake, task_fix, task_pr]


# ══════════════════════════════════════════════════════════════
#  CREW
# ══════════════════════════════════════════════════════════════

def build_crew() -> Crew:
    """Construct and return the Jira Solver Crew with sequential processing."""
    return Crew(
        agents=[
            ticket_intake_agent,
            technical_analyst_agent,
            codebase_navigator_agent,
            code_fixer_agent,
            pr_creator_agent,
            ticket_closer_agent,
        ],
        tasks=[
            task_intake,
            task_analyze,
            task_navigate,
            task_fix,
            task_pr,
            task_close,
        ],
        process=Process.sequential,
        verbose=True,
    )
