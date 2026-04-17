import os
import time

import httpx
from dotenv import load_dotenv, set_key

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(ENV_PATH)

BASE_URL = "https://www.strava.com/api/v3"
TOKEN_URL = "https://www.strava.com/oauth/token"


def _refresh_token() -> str:
    """Exchange refresh token for a new access token and persist to .env."""
    client_id = os.getenv("STRAVA_CLIENT_ID")
    client_secret = os.getenv("STRAVA_CLIENT_SECRET")
    refresh_token = os.getenv("STRAVA_REFRESH_TOKEN")

    with httpx.Client() as c:
        r = c.post(TOKEN_URL, data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        })

    if r.is_error:
        raise RuntimeError(f"Token refresh failed: {r.status_code} {r.text}")

    data = r.json()
    access_token = data["access_token"]
    new_refresh = data["refresh_token"]
    expires_at = str(data["expires_at"])

    set_key(ENV_PATH, "STRAVA_ACCESS_TOKEN", access_token)
    set_key(ENV_PATH, "STRAVA_REFRESH_TOKEN", new_refresh)
    set_key(ENV_PATH, "STRAVA_TOKEN_EXPIRES_AT", expires_at)

    os.environ["STRAVA_ACCESS_TOKEN"] = access_token
    os.environ["STRAVA_REFRESH_TOKEN"] = new_refresh
    os.environ["STRAVA_TOKEN_EXPIRES_AT"] = expires_at

    return access_token


def _access_token() -> str:
    """Return a valid access token, refreshing if expired."""
    expires_at = int(os.getenv("STRAVA_TOKEN_EXPIRES_AT", "0"))
    if time.time() >= expires_at:
        return _refresh_token()
    return os.getenv("STRAVA_ACCESS_TOKEN")


def get_client() -> httpx.Client:
    return httpx.Client(
        headers={
            "Authorization": f"Bearer {_access_token()}",
            "Accept": "application/json",
        },
        timeout=30,
    )


def handle_response(r: httpx.Response) -> str:
    """Return response text, or raise RuntimeError on 4xx/5xx."""
    if r.is_error:
        try:
            detail = r.json().get("message") or r.json()
        except Exception:
            detail = r.text or r.reason_phrase
        raise RuntimeError(f"HTTP {r.status_code}: {detail}")
    return r.text
