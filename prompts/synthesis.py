"""
synthesis.py — Builds the initial user message that kicks off the agent.

This is what the user "says" to Claude at the start of the conversation.
It packages together:
  - The job URL (for scraping)
  - The resume path (for parsing)
  - A clear instruction to begin the research loop
"""


def build_initial_message(job_url: str, resume_path: str) -> str:
    """
    Build the opening user message that starts the agent loop.

    Args:
        job_url:      The URL of the job posting to research
        resume_path:  Local path to the candidate's resume file

    Returns:
        A formatted string that becomes the first user message in
        the conversation Claude will respond to.
    """
    return f"""
Please research this job opportunity and write a tailored cover letter \
and interview talking points for me.

Job posting URL: {job_url}
Resume file path: {resume_path}

Follow your research process fully before writing anything:
  1. Scrape the job posting
  2. Parse my resume
  3. Run your web searches on the company
  4. Then write the cover letter and talking points

Be thorough. The more you learn about the company before writing, \
the better the output will be.
""".strip()
