"""
resume_parser.py — Extracts clean text from a resume file.

Supports:
  - PDF  (.pdf)  via pypdf
  - Plain text   (.txt, .md)  read directly

The extracted text is passed into the agent's context so Claude
can match the candidate's experience against the job requirements.
"""

import os
from pathlib import Path


def parse_resume(file_path: str) -> dict:
    """
    Extract text from a resume file.

    Returns:
        {"success": True,  "text": "...", "file": file_path}
      | {"success": False, "error": "...", "file": file_path}
    """
    path = Path(file_path)

    if not path.exists():
        return {"success": False, "error": f"File not found: {file_path}", "file": file_path}

    suffix = path.suffix.lower()

    # --- PDF ---
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            return {"success": False, "error": "pypdf not installed. Run: pip install pypdf", "file": file_path}

        try:
            reader = PdfReader(str(path))
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            full_text = "\n\n".join(pages)
        except Exception as e:
            return {"success": False, "error": f"PDF read error: {e}", "file": file_path}

    # --- Plain text / Markdown ---
    elif suffix in (".txt", ".md"):
        try:
            full_text = path.read_text(encoding="utf-8")
        except Exception as e:
            return {"success": False, "error": f"File read error: {e}", "file": file_path}

    else:
        return {
            "success": False,
            "error": f"Unsupported file type '{suffix}'. Use .pdf, .txt, or .md",
            "file": file_path,
        }

    full_text = full_text.strip()

    if not full_text:
        return {"success": False, "error": "Resume appears to be empty or unreadable.", "file": file_path}

    return {"success": True, "text": full_text, "file": file_path}
