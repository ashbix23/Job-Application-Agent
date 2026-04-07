"""
main.py — CLI entrypoint for the Job Application Agent.

Usage:
    python main.py <job_url> <resume_path> [--output-dir ./output]

Examples:
    python main.py "https://jobs.ashbyhq.com/acme/123" ./my_resume.pdf
    python main.py "https://greenhouse.io/jobs/456" ./resume.txt --output-dir ~/Desktop
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

from agent import run_agent

load_dotenv()
console = Console()


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI agent that researches a job and writes a tailored cover letter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "job_url",
        help="Full URL of the job posting to research.",
    )
    parser.add_argument(
        "resume_path",
        help="Path to your resume file (.pdf, .txt, or .md).",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Directory to write output files (default: ./output).",
    )
    return parser.parse_args()


def check_env():
    """Fail fast with helpful messages if API keys are missing."""
    missing = []
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if not os.getenv("SERPER_API_KEY"):
        missing.append("SERPER_API_KEY")

    if missing:
        console.print(Panel(
            "\n".join([
                f"[red]Missing environment variable(s): {', '.join(missing)}[/]",
                "",
                "Copy .env.example to .env and fill in your keys:",
                "  [cyan]cp .env.example .env[/]",
                "",
                "Get your keys at:",
                "  Anthropic → https://console.anthropic.com/",
                "  Serper    → https://serper.dev/",
            ]),
            title="[bold red]Configuration Error[/]",
            border_style="red",
        ))
        sys.exit(1)

def check_resume(resume_path: str):
    """Fail fast if the resume file doesn't exist."""
    if not Path(resume_path).exists():
        console.print(Panel(
            f"[red]Resume file not found:[/] {resume_path}\n\n"
            "Check the path and try again.",
            title="[bold red]File Not Found[/]",
            border_style="red",
        ))
        sys.exit(1)


def save_output(content: str, output_dir: str, job_url: str):
    """
    Write the agent's output to timestamped markdown files.
    Splits the single response into cover_letter.md and talking_points.md.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Split on the talking points header if present
    if "# Interview Talking Points" in content:
        parts = content.split("# Interview Talking Points", 1)
        cover_letter   = parts[0].strip()
        talking_points = ("# Interview Talking Points" + parts[1]).strip()
    else:
        cover_letter   = content
        talking_points = ""

    # Write cover letter
    cl_file = out_path / f"cover_letter_{timestamp}.md"
    cl_file.write_text(cover_letter, encoding="utf-8")

    # Write talking points
    if talking_points:
        tp_file = out_path / f"talking_points_{timestamp}.md"
        tp_file.write_text(talking_points, encoding="utf-8")
    else:
        tp_file = None

    return cl_file, tp_file


def main():
    args = parse_args()

    check_env()
    check_resume(args.resume_path)

    console.rule("[bold cyan]Job Application Agent[/]")
    console.print()

    # Run the agent
    try:
        output = run_agent(
            job_url=args.job_url,
            resume_path=args.resume_path,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/]")
        sys.exit(0)
    except Exception as e:
        console.print(Panel(
            f"[red]Agent error:[/] {e}",
            title="[bold red]Error[/]",
            border_style="red",
        ))
        sys.exit(1)

    # Print output to terminal
    console.rule("[bold green]Output[/]")
    console.print(output)
    console.rule()

    # Save to files
    cl_file, tp_file = save_output(output, args.output_dir, args.job_url)

    console.print()
    console.print(Panel(
        "\n".join([
            f"[green]✓[/] Cover letter   → [cyan]{cl_file}[/]",
            f"[green]✓[/] Talking points → [cyan]{tp_file}[/]" if tp_file else "",
        ]).strip(),
        title="[bold green]Files Saved[/]",
        border_style="green",
    ))


if __name__ == "__main__":
    main()
