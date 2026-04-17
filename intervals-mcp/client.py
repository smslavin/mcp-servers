import os

import httpx
from dotenv import load_dotenv

load_dotenv()

ATHLETE_ID = os.getenv("INTERVALS_ATHLETE_ID")
API_KEY = os.getenv("INTERVALS_API_KEY")
BASE_URL = "https://intervals.icu/api/v1"


def get_client() -> httpx.Client:
    return httpx.Client(
        auth=("API_KEY", API_KEY),
        headers={"Accept": "application/json"},
        timeout=30,
    )


def athlete_id(override: str | None) -> str:
    return override or ATHLETE_ID


def handle_response(r: httpx.Response) -> str:
    """Return response text, or raise a RuntimeError on 4xx/5xx.

    Raising instead of returning an error string ensures the MCP client
    receives a protocol-level error with the exact message rather than
    having the AI model paraphrase the error as tool output.
    """
    if r.is_error:
        try:
            detail = r.json().get("error") or r.json()
        except Exception:
            detail = r.text or r.reason_phrase
        raise RuntimeError(f"HTTP {r.status_code}: {detail}")
    return r.text
