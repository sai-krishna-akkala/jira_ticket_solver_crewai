<div align="center">

# 🤖 Jira Solver Crew

### **Autonomous AI Bug-Fix Pipeline powered by CrewAI + Ollama**

[![CrewAI](https://img.shields.io/badge/CrewAI-1.12-blue?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6IiBmaWxsPSJ3aGl0ZSIvPjwvc3ZnPg==&labelColor=1a1a2e)](https://www.crewai.com/)
[![Ollama](https://img.shields.io/badge/Ollama-llama3.2-green?style=for-the-badge&labelColor=0d1117)](https://ollama.com/)
[![Python](https://img.shields.io/badge/Python-3.21+-yellow?style=for-the-badge&logo=python&labelColor=1a1a2e)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge&labelColor=1a1a2e)]()

<br>

> **6 AI agents work together to read Jira tickets, analyze bugs, navigate code, write fixes, create git branches, and close tickets — fully autonomously.**

<br>

<img src="https://img.shields.io/badge/🎫_Ticket_Intake-blue?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/→-gray?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/🔍_Analyze-teal?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/→-gray?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/📂_Navigate-orange?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/→-gray?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/🛠_Fix_Code-red?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/→-gray?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/🌿_Git_PR-green?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/→-gray?style=flat-square" height="28"/>
<img src="https://img.shields.io/badge/✅_Close_Ticket-purple?style=flat-square" height="28"/>

</div>

---

## 🏗️ Architecture Diagram

```mermaid
graph TB
    subgraph USER["🧑‍💻 USER"]
        style USER fill:#1a1a2e,stroke:#e94560,color:#fff,stroke-width:2px
        RUN["python main.py"]
    end

    subgraph ORCHESTRATOR["⚙️ CREW ORCHESTRATOR"]
        style ORCHESTRATOR fill:#0f3460,stroke:#16c79a,color:#fff,stroke-width:2px
        MAIN["main.py<br/>🔄 Loop until all tickets resolved"]
        CREW["crew.py<br/>Sequential Process Engine"]
    end

    subgraph AGENTS["🤖 6 AI AGENTS"]
        style AGENTS fill:#162447,stroke:#e94560,color:#fff,stroke-width:2px
        A1["🎫 Ticket Intake<br/>Specialist"]
        A2["🔍 Technical<br/>Analyst"]
        A3["📂 Codebase<br/>Navigator"]
        A4["🛠️ Code<br/>Fixer"]
        A5["🌿 PR<br/>Creator"]
        A6["✅ Ticket<br/>Closer"]
    end

    subgraph LLM["🧠 LLM ENGINE"]
        style LLM fill:#1b1b2f,stroke:#e23e57,color:#fff,stroke-width:2px
        OLLAMA["Ollama Server<br/>localhost:11434"]
        LLAMA["🦙 llama3.2<br/>70B Versatile"]
    end

    subgraph TOOLS["🔧 CUSTOM TOOLS"]
        style TOOLS fill:#1a1a2e,stroke:#00b8a9,color:#fff,stroke-width:2px
        T1["📖 TicketReaderTool"]
        T2["📄 CodeReaderTool"]
        T3["✏️ CodeWriterTool"]
        T4["🌿 GitTool"]
        T5["📝 TicketUpdaterTool"]
    end

    subgraph DATA["📁 DATA LAYER"]
        style DATA fill:#2d132c,stroke:#ee4540,color:#fff,stroke-width:2px
        TICKETS["tickets.json<br/>🎫 Bug Tickets"]
        CODEBASE["project_codebase/<br/>🐛 Buggy Source Code"]
        OUTPUT["output/<br/>✅ Fixed Code + Logs"]
    end

    RUN --> MAIN
    MAIN --> CREW
    CREW --> A1 --> A2 --> A3 --> A4 --> A5 --> A6

    A1 -.->|uses| T1
    A3 -.->|uses| T2
    A4 -.->|uses| T2
    A4 -.->|uses| T3
    A5 -.->|uses| T4
    A6 -.->|uses| T5

    A1 & A2 & A3 & A4 & A5 & A6 ====>|API calls| OLLAMA
    OLLAMA --> LLAMA

    T1 -->|reads| TICKETS
    T2 -->|reads| CODEBASE
    T3 -->|writes| OUTPUT
    T4 -->|commits| OUTPUT
    T5 -->|updates| TICKETS

    linkStyle 0,1,2,3,4,5,6,7 stroke:#e94560,stroke-width:2px
    linkStyle 8,9,10,11,12,13 stroke:#00b8a9,stroke-width:2px,stroke-dasharray:5
    linkStyle 14 stroke:#e23e57,stroke-width:3px
    linkStyle 15 stroke:#e23e57,stroke-width:3px
    linkStyle 16,17,18,19,20 stroke:#ee4540,stroke-width:2px
```

---

## 🔄 Execution Flow Diagram

```mermaid
flowchart TD
    START(["🚀 START<br/>python main.py"])
    style START fill:#e94560,stroke:#fff,color:#fff,stroke-width:2px

    CHECK{"🔍 Any open<br/>tickets?"}
    style CHECK fill:#f39c12,stroke:#fff,color:#fff,stroke-width:2px

    DONE(["🎉 ALL TICKETS<br/>RESOLVED!"])
    style DONE fill:#16c79a,stroke:#fff,color:#fff,stroke-width:2px

    subgraph PIPELINE["🔄 AGENT PIPELINE — One Ticket Per Iteration"]
        style PIPELINE fill:#0f3460,stroke:#16c79a,color:#fff,stroke-width:2px

        S1["🎫 STEP 1: Ticket Intake<br/>━━━━━━━━━━━━━━━━━━<br/>📖 Read tickets.json<br/>🔢 Sort by priority P0→P1→P2<br/>📤 Return top open ticket"]
        style S1 fill:#e94560,stroke:#fff,color:#fff

        S2["🔍 STEP 2: Technical Analysis<br/>━━━━━━━━━━━━━━━━━━━<br/>📋 Parse ticket description<br/>🧠 Identify root cause<br/>📝 Write technical specification"]
        style S2 fill:#e94560,stroke:#fff,color:#fff

        S3["📂 STEP 3: Code Navigation<br/>━━━━━━━━━━━━━━━━━━<br/>📄 Read linked source file<br/>🔎 Find buggy function & lines<br/>💡 Explain what's wrong"]
        style S3 fill:#f39c12,stroke:#fff,color:#fff

        S4["🛠️ STEP 4: Code Fix<br/>━━━━━━━━━━━━━━━━━━<br/>✏️ Write minimal correct fix<br/>📁 Save to output/fixed_*.py<br/>📊 Generate before/after diff"]
        style S4 fill:#f39c12,stroke:#fff,color:#fff

        S5["🌿 STEP 5: Git PR<br/>━━━━━━━━━━━━━━━━━━<br/>🌿 Create fix/JIRA-XXX branch<br/>💾 Commit fixed file<br/>📝 Write PR summary markdown"]
        style S5 fill:#16c79a,stroke:#fff,color:#fff

        S6["✅ STEP 6: Close Ticket<br/>━━━━━━━━━━━━━━━━━━<br/>📝 Set status → done<br/>👤 Assign to AI Crew<br/>📊 Log to resolution_log.json"]
        style S6 fill:#16c79a,stroke:#fff,color:#fff

        S1 --> S2 --> S3 --> S4 --> S5 --> S6
    end

    START --> CHECK
    CHECK -->|"✅ Yes — tickets remain"| S1
    S6 --> CHECK
    CHECK -->|"🎉 No — all done!"| DONE

    linkStyle 0,1,2,3,4 stroke:#e94560,stroke-width:3px
    linkStyle 5,6 stroke:#16c79a,stroke-width:3px
    linkStyle 7 stroke:#f39c12,stroke-width:3px
```

---

## 📁 Project Structure

```
jira_solver_crew/
│
├── 🚀 main.py                    # Entry point — loops until all tickets resolved
├── 🤖 crew.py                    # 6 agents + 6 tasks + sequential crew
│
├── ⚙️ config/
│   └── llm_config.py             # Ollama llama3.2 configuration
│
├── 🔧 tools/
│   ├── ticket_reader.py          # Read + prioritize tickets.json
│   ├── code_reader.py            # Read source files with line numbers
│   ├── code_writer.py            # Write fixed code to output/
│   ├── git_tool.py               # Create branch + commit + PR summary
│   └── ticket_updater.py         # Update ticket status + resolution log
│
├── 🐛 project_codebase/
│   ├── auth/
│   │   └── login.py              # Bug: case-sensitive email lookup
│   └── forms/
│       └── signup.py             # Bug: no phone number validation
│
├── 🎫 tickets.json               # Simulated Jira board (3 tickets)
│
└── 📦 output/                    # Generated by the crew
    ├── fixed_login.py            # ✅ Corrected login code
    ├── fixed_signup.py           # ✅ Corrected signup code
    ├── pr_summary.md             # 📝 Pull request description
    └── resolution_log.json       # 📊 Resolution audit trail
```

---

## 🤖 The 6 Agents

| # | Agent | Role | LLM | Tools |
|:-:|-------|------|:---:|-------|
| 🎫 | **Ticket Intake Specialist** | Reads tickets.json, sorts by priority, returns top open ticket | llama3.2 | `TicketReaderTool` |
| 🔍 | **Technical Ticket Analyst** | Converts ticket description into precise technical specification | llama3.2 | — |
| 📂 | **Codebase Navigator** | Reads source files, finds exact buggy function and line numbers | llama3.2 | `CodeReaderTool` |
| 🛠️ | **Autonomous Code Fixer** | Writes minimal correct fix and saves to output folder | llama3.2 (temp=0.1) | `CodeReaderTool`, `CodeWriterTool` |
| 🌿 | **PR Creator** | Creates git branch, commits fix, writes PR summary markdown | llama3.2 | `GitTool` |
| ✅ | **Ticket Closer** | Marks ticket as done, updates resolution log | llama3.2 | `TicketUpdaterTool` |

---

## 🎫 Sample Tickets

| ID | Priority | Status | Bug | File |
|----|:--------:|:------:|-----|------|
| `JIRA-101` | 🔴 P0 | 🔄 open | Case-sensitive email login | `auth/login.py` |
| `JIRA-102` | 🟠 P1 | 🔄 open | No phone number validation | `forms/signup.py` |
| `JIRA-100` | 🟡 P2 | ✅ done | *(previously resolved by human)* | `forms/signup.py` |

---

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.21+ | Runtime |
| **Ollama** | Latest | Local LLM server |
| **Git** | Optional | Real branch/commit (has fallback) |

### 1. Install Ollama & Pull Model

```bash
# Install Ollama from https://ollama.com
ollama pull llama3.2
ollama serve              # keep running in a terminal
```

### 2. Setup Python Environment

```bash
cd jira_solver_crew
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # macOS/Linux

pip install crewai crewai-tools gitpython
```

### 3. Run the Crew

```bash
python main.py
```

The crew **loops automatically** until all open tickets are resolved:

```
============================================================
  JIRA SOLVER CREW — Autonomous Bug Fix Pipeline
  Runs until ALL open tickets are resolved
============================================================

Pipeline: Intake → Analyze → Navigate → Fix → PR → Close

------------------------------------------------------------
  🔄 ITERATION 1  |  2 open ticket(s) remaining
  Next up: JIRA-101 — Login fails for mixed-case emails
------------------------------------------------------------

  ✓ Iteration 1 complete

------------------------------------------------------------
  🔄 ITERATION 2  |  1 open ticket(s) remaining
  Next up: JIRA-102 — Signup accepts invalid phone numbers
------------------------------------------------------------

  ✓ Iteration 2 complete

============================================================
  ✅ ALL TICKETS RESOLVED — No open tickets remaining!
============================================================
```

---

## 🔧 Custom Tools Reference

| Tool | File | Description |
|------|------|-------------|
| `read_tickets` | `tools/ticket_reader.py` | Reads `tickets.json`, filters open, sorts by priority, returns top ticket |
| `read_code_file` | `tools/code_reader.py` | Reads any source file with line numbers prepended |
| `write_code_file` | `tools/code_writer.py` | Writes code content to `output/` folder |
| `git_commit` | `tools/git_tool.py` | Creates branch, commits fix, writes PR summary *(fallback if Git not installed)* |
| `update_ticket` | `tools/ticket_updater.py` | Sets ticket status to done, appends to resolution log |

---

## ⚠️ Important Notes

> **Model Compatibility** — `llama3.2` support tool/function calling in Ollama. `llama3` and `codellama` do **NOT** work with CrewAI tools.

> **One Ticket Per Loop** — Each iteration resolves the single highest-priority open ticket. The main loop continues until zero remain.

> **Git Fallback** — If Git is not installed, the `GitTool` simulates branch/commit operations and still generates `pr_summary.md`.

---

## 📊 Output Files

After a successful run, check the `output/` folder:

| File | Contents |
|------|----------|
| `fixed_login.py` | Corrected login code (case-insensitive email) |
| `fixed_signup.py` | Corrected signup code (phone validation regex) |
| `pr_summary.md` | Pull request description with ticket ID, changes, and test steps |
| `resolution_log.json` | Timestamped resolution entries for each closed ticket |

---

## 🧩 How to Add Your Own Tickets

Edit `tickets.json` to add new bug tickets:

```json
{
  "id": "JIRA-200",
  "type": "bug",
  "priority": "P0",
  "status": "open",
  "title": "Your bug title here",
  "description": "Detailed description of what's broken and expected behavior.",
  "linked_file": "project_codebase/path/to/file.py",
  "assigned_to": null,
  "resolution_branch": null
}
```

Then add the buggy source file under `project_codebase/` and run `python main.py`.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

**Built with using [CrewAI](https://www.crewai.com/) + [Ollama](https://ollama.com/) + [llama3.2](https://llama.meta.com/)**

<br>

<img src="https://img.shields.io/badge/Made_with-CrewAI-blue?style=for-the-badge" height="30"/>
&nbsp;
<img src="https://img.shields.io/badge/Powered_by-Ollama-green?style=for-the-badge" height="30"/>
&nbsp;
<img src="https://img.shields.io/badge/Model-llama3.2-red?style=for-the-badge" height="30"/>

</div>
