"""
CodeWriterTool — Writes fixed code to the output/ folder.
"""

import os
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")


class CodeWriterToolSchema(BaseModel):
    filename: str = Field(..., description="Output filename, e.g. 'fixed_login.py'")
    code: str = Field(..., description="The full corrected source code to write")


class CodeWriterTool(BaseTool):
    name: str = "write_code_file"
    description: str = (
        "Writes code content to a file inside the output/ folder. "
        "Pass 'filename' (e.g. 'fixed_login.py') and 'code' (the full file content)."
    )
    args_schema: type[BaseModel] = CodeWriterToolSchema

    def _normalize_filename(self, filename: str) -> str:
        normalized = filename.strip().replace("\\", "/")
        if not normalized:
            raise ValueError("filename cannot be empty")

        if normalized.startswith("output/"):
            normalized = normalized[len("output/") :]

        if os.path.isabs(filename) or os.path.isabs(normalized):
            raise ValueError("absolute paths are not allowed")

        normalized = os.path.normpath(normalized).replace("\\", "/")
        if normalized in ("", ".", "..") or normalized.startswith("../"):
            raise ValueError("path traversal is not allowed")

        return normalized

    def _run(self, filename: str, code: str, **kwargs) -> str:
        try:
            safe_filename = self._normalize_filename(filename)
        except ValueError as error:
            return f"ERROR: Invalid filename '{filename}' ({error})"

        output_root = os.path.abspath(OUTPUT_DIR)
        os.makedirs(output_root, exist_ok=True)

        file_path = os.path.abspath(os.path.join(output_root, safe_filename))
        if os.path.commonpath([output_root, file_path]) != output_root:
            return f"ERROR: Invalid filename '{filename}' (must stay inside output/)"

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        return f"SUCCESS: Wrote {len(code)} bytes to output/{safe_filename}"
