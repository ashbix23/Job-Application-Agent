# Job Application Agent

An autonomous AI agent that researches a job posting and writes a tailored cover letter and interview talking points in one command.

You give it a job URL and your resume. It scrapes the posting, researches the company, reads your resume, and produces ready-to-use output.

---

## How It Works

```
python main.py <job_url> <resume_path>
```

The agent runs a full research loop before writing anything:

1. **Scrapes** the job posting from the URL
2. **Parses** your resume
3. **Researches** the company — culture, tech stack, recent news
4. **Writes** a tailored cover letter + interview talking points

Output is saved as two markdown files in `./output/`.

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/ashbix23/Job-Application-Agent.git
cd job-agent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API keys
```bash
cp .env.example .env
```

Then open `.env` and fill in:

| Key | Where to get it |
|-----|----------------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/ |
| `SERPER_API_KEY` | https://serper.dev/ — free tier: 2,500 searches |

---

## Usage

```bash
python main.py <job_url> <resume_path> [--output-dir ./output]
```

### Examples

```bash
# PDF resume
python main.py "https://jobs.ashbyhq.com/acme/engineer-123" ./my_resume.pdf

# Plain text resume
python main.py "https://greenhouse.io/jobs/456" ./resume.txt

# Custom output directory
python main.py "https://lever.co/company/role" ./resume.pdf --output-dir ~/Desktop
```

---

## Output

Each run produces two timestamped files in your output directory:

```
output/
├── cover_letter_20250406_143022.md
└── talking_points_20250406_143022.md
```

**Cover letter** — 3–4 paragraphs, specific to the company and role, ready to send.

**Talking points** — structured prep notes covering:
- Why this company
- Why this role
- Your strongest fit areas
- How to address any gaps
- Questions to ask the interviewer

---

## Project Structure

```
job-agent/
├── main.py              # CLI entrypoint
├── agent.py             # Agentic loop — manages tool calling
├── tools/
│   ├── __init__.py      # Tool registry and dispatcher
│   ├── scraper.py       # Scrapes job postings
│   ├── search.py        # Brave Search API integration
│   └── resume_parser.py # Extracts text from PDF / .txt resumes
├── prompts/
│   ├── system.py        # Agent system prompt
│   └── synthesis.py     # Initial message builder
├── output/              # Generated cover letters and talking points
├── .env.example         # API key template
└── requirements.txt
```

---

## Requirements

- Python 3.9+
- Anthropic API key
- Serper API key

---

## Supported Resume Formats

- `.pdf`
- `.txt`
- `.md`
