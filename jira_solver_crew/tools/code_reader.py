"""
CodeReaderTool — Reads any source file and returns its content with line numbers.
"""

import os
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")


class CodeReaderToolSchema(BaseModel):
    file_path: str = Field(..., description="Relative path to the source file, e.g. 'project_codebase/auth/login.py'")


class CodeReaderTool(BaseTool):
    name: str = "read_code_file"
    description: str = (
        "Reads a source file from the project codebase and returns its "
        "content with line numbers prepended. Pass the relative path "
        "(e.g. 'project_codebase/auth/login.py')."
    )
    args_schema: type[BaseModel] = CodeReaderToolSchema

    def _run(self, file_path: str, **kwargs) -> str:
        full_path = os.path.join(PROJECT_ROOT, file_path)
        full_path = os.path.abspath(full_path)

        if not os.path.exists(full_path):
            return f"ERROR: File not found — {file_path}"

        with open(full_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        numbered = [f"{i+1:4d} | {line}" for i, line in enumerate(lines)]
        return "".join(numbered)
