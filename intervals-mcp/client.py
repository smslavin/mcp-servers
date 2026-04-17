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
    """Return response text, or a descriptive error string on 4xx/5xx."""
    if r.is_error:
        try:
            detail = r.json()
        except Exception:
            detail = r.text or r.reason_phrase
        return f"Error {r.status_code} from {r.url}: {detail}"
    return r.text
