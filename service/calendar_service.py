import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from core.logging import get_logger

load_dotenv()

logger = get_logger(__name__)

SCOPES = os.getenv('SCOPES')
TOKEN_FILE = Path("token.json")

def get_service():
    """Build an authenticated Calendar API client. Refreshes token if needed."""
    if not TOKEN_FILE.exists():
        raise RuntimeError("token.json missing — run scripts/google_auth.py first")

    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_FILE.write_text(creds.to_json())
            logger.info("[CAL] refreshed access token")
        else:
            raise RuntimeError("token invalid; re-run scripts/google_auth.py")

    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def create_event(
    summary: str,
    start: datetime,
    end: datetime,
    description: str | None = None,
    location: str | None = None,
) -> str:
    """Create an event on the user's primary calendar. Returns the event link."""
    service = get_service()
    body = {
        "summary": summary,
        "start": {"dateTime": start.isoformat()},
        "end":   {"dateTime": end.isoformat()},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location

    event = service.events().insert(calendarId="primary", body=body).execute()
    logger.info("[CAL] created event %s: %s", event["id"], summary)
    return event.get("htmlLink", "(no link)")


def list_events(time_min: datetime, time_max: datetime) -> list[dict]:
    """List events between two datetime on the primary calendar."""
    service = get_service()
    result = service.events().list(
        calendarId="primary",
        timeMin=time_min.isoformat(),
        timeMax=time_max.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    return result.get("items", [])


def update_event(
    event_id: str,
    summary: str | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    description: str | None = None,
    location: str | None = None,
) -> str:
    """Update fields on an existing event. Only provided fields change."""
    service = get_service()

    # Fetch first so we only patch what's given (Google's API is PATCH-friendly via patch())
    body: dict = {}
    if summary is not None:
        body["summary"] = summary
    if description is not None:
        body["description"] = description
    if location is not None:
        body["location"] = location
    if start is not None:
        body["start"] = {"dateTime": start.isoformat()}
    if end is not None:
        body["end"] = {"dateTime": end.isoformat()}

    if not body:
        raise ValueError("nothing to update")

    event = service.events().patch(
        calendarId="primary", eventId=event_id, body=body
    ).execute()
    logger.info("[CAL] updated event %s", event_id)
    return event.get("htmlLink", "(no link)")


def delete_event(event_id: str) -> None:
    """Delete an event by ID."""
    service = get_service()
    service.events().delete(calendarId="primary", eventId=event_id).execute()
    logger.info("[CAL] deleted event %s", event_id)