"""
scraper.py — Fetches and cleans a job posting from a URL.

Strategy:
  1. Fetch raw HTML via httpx with a realistic browser User-Agent
  2. Parse with BeautifulSoup, stripping nav/footer/cookie noise
  3. Convert to clean Markdown via html2text
  4. Truncate to a safe token budget (~6000 words)
"""

import httpx
from bs4 import BeautifulSoup
import html2text

_NOISE_TAGS = [
    "nav", "header", "footer", "aside", "script", "style",
    "noscript", "iframe", "form", "button", "svg",
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_MAX_WORDS = 6000


def scrape_job_page(url: str) -> dict:
    """
    Fetch a job posting URL and return cleaned text.

    Returns:
        {"success": True,  "text": "...", "url": url}
      | {"success": False, "error": "...", "url": url}
    """
    try:
        with httpx.Client(follow_redirects=True, timeout=20, headers=_HEADERS) as client:
            response = client.get(url)
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        return {"success": False, "error": f"HTTP {e.response.status_code}", "url": url}
    except httpx.RequestError as e:
        return {"success": False, "error": f"Request failed: {e}", "url": url}

    soup = BeautifulSoup(response.text, "html.parser")

    # Strip noisy structural tags
    for tag in soup(_NOISE_TAGS):
        tag.decompose()

    # Try to narrow to the main content area
    main = (
        soup.find("main")
        or soup.find("article")
        or soup.find(id="job-description")
        or soup.find(class_="job-description")
        or soup.find(attrs={"data-testid": "job-description"})
        or soup.body
        or soup
    )

    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.body_width = 0  # no line wrapping
    markdown = converter.handle(str(main))

    # Collapse excess blank lines
    lines = markdown.splitlines()
    cleaned_lines = []
    prev_blank = False
    for line in lines:
        is_blank = not line.strip()
        if is_blank and prev_blank:
            continue
        cleaned_lines.append(line)
        prev_blank = is_blank

    text = "\n".join(cleaned_lines).strip()

    # Truncate to token budget
    words = text.split()
    if len(words) > _MAX_WORDS:
        text = " ".join(words[:_MAX_WORDS]) + "\n\n[... truncated for length ...]"

    return {"success": True, "text": text, "url": url}
