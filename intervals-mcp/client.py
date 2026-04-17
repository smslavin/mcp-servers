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
