import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Client(api_key=API_KEY)

SYSTEM_PROMPT = """
You are an expert curator of beginner-friendly learning resources, images, and videos.
1. For any topic, find top tutorials/articles, infographic images, and video URLs for beginners.
2. Present only numbered URLs in your output, minimizing all extra text.
3. Prefer diverse types: articles, images/diagrams, video tutorials.
4. Rank by beginner accessibility, practical clarity, and relevance.
5. If not enough images or videos exist, fill the list with the best available beginner articles.
6. No commentary, description, or markdown—output URLs only.
"""


def claude_complete(messages, model="claude-haiku-4-5", max_tokens=1024):
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.2,
        system=SYSTEM_PROMPT,
        messages=messages
    )
    return response.content[0].text


def run_search(topic):
    prompt = (
        f"List up to 10 top beginner-friendly URLs about {topic}. "
        "Include at least 1 tutorial article, 1 infographic/image, and 1 video if available. Number the results."
    )
    return claude_complete([{"role": "user", "content": prompt}])


def run_fetch(url):
    prompt = (
        f"Summarize the page at {url} for beginners. Note: Is this a tutorial, infographic/image, or video? Rate beginner-friendliness."
    )
    return claude_complete([{"role": "user", "content": prompt}])


def run_rank(url_summaries):
    prompt = (
        "Given these resource summaries, select and list the best 3-5 for beginners. "
        "Prioritize articles, images/infographics, and videos. Output strictly numbered URLs only:\n"
        f"{url_summaries}"
    )
    return claude_complete([{"role": "user", "content": prompt}])


def run_playwright_fetch(url):
    prompt = (
        f"Using the Playwright MCP browser, fetch and summarize the page at {url} for beginners. "
        "Note if it contains tutorial, infographic/image, or video. Rate beginner accessibility."
    )
    return claude_complete([{"role": "user", "content": prompt}])


def fetch_with_fallback(url):
    try:
        summary = run_fetch(url)
        if "blocked" in summary.lower() or "error" in summary.lower():
            summary = run_playwright_fetch(url)
        return summary
    except Exception:
        return run_playwright_fetch(url)
