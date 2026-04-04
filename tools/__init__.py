"""
tools/__init__.py — Tool registry.

Two things live here:
  1. TOOL_SCHEMAS  — the JSON schema definitions Claude uses to decide
                     when and how to call each tool
  2. run_tool()    — the dispatcher that executes whichever tool
                     Claude asks for and returns the result
"""

from tools.scraper import scrape_job_page
from tools.search import web_search
from tools.resume_parser import parse_resume


# ── Tool Schemas ────────────────────────────────────────────────────────────
# These are passed to the Anthropic API on every request so Claude knows
# what tools are available and what arguments each one expects.

TOOL_SCHEMAS = [
    {
        "name": "scrape_job_page",
        "description": (
            "Fetches a job posting from a URL and returns the cleaned text. "
            "Use this first to get the full job description."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The full URL of the job posting to scrape.",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "web_search",
        "description": (
            "Search the web for information about a company or role. "
            "Use this to research company culture, mission, tech stack, "
            "recent news, and anything else that will strengthen the cover letter."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific for better results.",
                },
                "num_results": {
                    "type": "integer",
                    "description": "Number of results to return. Default is 5, max is 10.",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "parse_resume",
        "description": (
            "Extracts and returns the text content of the candidate's resume. "
            "Use this to understand the candidate's experience, skills, and background "
            "before writing the cover letter."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The local file path to the resume (.pdf, .txt, or .md).",
                },
            },
            "required": ["file_path"],
        },
    },
]


# ── Tool Dispatcher ──────────────────────────────────────────────────────────
# Claude returns a tool name + input dict. We map that to the real function.

def run_tool(tool_name: str, tool_input: dict) -> str:
    """
    Execute a tool by name and return its result as a string.
    The string gets sent back to Claude as the tool_result content.
    """
    if tool_name == "scrape_job_page":
        result = scrape_job_page(tool_input["url"])

    elif tool_name == "web_search":
        result = web_search(
            query=tool_input["query"],
            num_results=tool_input.get("num_results", 5),
        )

    elif tool_name == "parse_resume":
        result = parse_resume(tool_input["file_path"])

    else:
        result = {"success": False, "error": f"Unknown tool: {tool_name}"}

    # Format results cleanly for Claude to read back
    if tool_name == "web_search" and result.get("success"):
        lines = [f"Search results for: '{result['query']}'\n"]
        for i, r in enumerate(result["results"], 1):
            lines.append(f"{i}. {r['title']}")
            lines.append(f"   {r['url']}")
            lines.append(f"   {r['snippet']}\n")
        return "\n".join(lines)

    if not result.get("success"):
        return f"Error: {result.get('error', 'Unknown error')}"

    return result.get("text", str(result))
