"""
agent.py — Core agentic loop.

Manages the back-and-forth between Claude and the tools until
Claude decides it has enough research to write the final output.

Flow:
  1. Send initial message + system prompt to Claude
  2. Claude responds with tool calls
  3. We execute each tool and send results back
  4. Repeat until Claude stops calling tools
  5. Return Claude's final text response
"""

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live

from tools import TOOL_SCHEMAS, run_tool
from prompts.system import SYSTEM_PROMPT
from prompts.synthesis import build_initial_message

console = Console()

MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 8096
MAX_ITERATIONS = 20  # safety cap — prevents runaway loops


def run_agent(job_url: str, resume_path: str) -> str:
    """
    Run the full research + writing agent loop.

    Args:
        job_url:      URL of the job posting
        resume_path:  Local path to the resume file

    Returns:
        The final markdown string containing the cover letter
        and talking points.
    """
    client = anthropic.Anthropic()

    messages = [
        {
            "role": "user",
            "content": build_initial_message(job_url, resume_path),
        }
    ]

    console.print(Panel(
        f"[bold cyan]Job URL:[/] {job_url}\n[bold cyan]Resume:[/] {resume_path}",
        title="[bold]Job Application Agent[/]",
        border_style="cyan",
    ))

    iteration = 0

    while iteration < MAX_ITERATIONS:
        iteration += 1

        # ── Call Claude ──────────────────────────────────────────────────
        with Live(Spinner("dots", text=" Thinking..."), refresh_per_second=10, console=console):
            response = client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=TOOL_SCHEMAS,
                messages=messages,
            )

        # ── Check stop reason ────────────────────────────────────────────
        if response.stop_reason == "end_turn":
            # Claude is done — extract the final text response
            final_text = _extract_text(response)
            console.print("\n[bold green]✓ Research complete. Output generated.[/]\n")
            return final_text

        if response.stop_reason != "tool_use":
            # Unexpected stop — return whatever text we have
            console.print(f"[yellow]Unexpected stop reason: {response.stop_reason}[/]")
            return _extract_text(response)

        # ── Process tool calls ───────────────────────────────────────────
        # Add Claude's response (with tool calls) to message history
        messages.append({"role": "assistant", "content": response.content})

        # Build the tool_result messages to send back
        tool_results = []

        for block in response.content:
            if block.type != "tool_use":
                continue

            tool_name  = block.name
            tool_input = block.input
            tool_id    = block.id

            console.print(f"[bold yellow]→ Tool:[/] {tool_name}", end="")
            if "url" in tool_input:
                console.print(f"  [dim]{tool_input['url']}[/]")
            elif "query" in tool_input:
                console.print(f"  [dim]{tool_input['query']}[/]")
            elif "file_path" in tool_input:
                console.print(f"  [dim]{tool_input['file_path']}[/]")
            else:
                console.print()

            # Run the tool
            result_text = run_tool(tool_name, tool_input)

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": result_text,
            })

        # Send all tool results back to Claude in one message
        messages.append({
            "role": "user",
            "content": tool_results,
        })

    # If we hit MAX_ITERATIONS, return whatever the last response was
    console.print("[red]Warning: hit max iterations limit.[/]")
    return _extract_text(response)


def _extract_text(response: anthropic.types.Message) -> str:
    """Pull all text blocks out of a Claude response into one string."""
    parts = []
    for block in response.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n\n".join(parts).strip()
