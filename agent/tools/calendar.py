from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pydantic_ai import Agent
from service.calendar_service import create_event, list_events, update_event, delete_event
from core.logging import get_logger

logger = get_logger(__name__)
TZ= ZoneInfo('Asia/Jerusalem')

def register(agent: Agent) -> None:

    @agent.tool_plain
    async def schedule_meeting(
        title: str,
        start_iso: str,
        end_iso: str | None = None,
        description: str | None = None,
        location: str | None = None,
    ) -> str:
        """Schedule a meeting on the user's Google Calendar.

        Args:
            title: Short event title (e.g. "Lunch with Dani").
            start_iso: Start time as ISO 8601 with timezone offset,
                e.g. "2026-04-16T13:00:00+03:00". Resolve relative times
                ("tomorrow at 1pm") using the current time in the system prompt.
            end_iso: End time, same format. If omitted, defaults to one hour after start.
            description: Optional details or agenda.
            location: Optional location or video link.
        """
        start = datetime.fromisoformat(start_iso)
        if start.tzinfo is None:
            start = start.replace(tzinfo=TZ)

        if end_iso:
            end = datetime.fromisoformat(end_iso)
            if end.tzinfo is None:
                end = end.replace(tzinfo=TZ)
        else:
            end = start + timedelta(hours=1)

        if start < datetime.now(TZ):
            return f"That time ({start:%Y-%m-%d %H:%M}) is in the past."

        link = create_event(title, start, end, description, location)
        return f"Scheduled '{title}' on {start:%a %d %b at %H:%M}. {link}"

    @agent.tool_plain
    async def list_upcoming_events(days_ahead: int = 7) -> str:
        """List upcoming calendar events.

        Args:
            days_ahead: How many days into the future to look. Default 7.
        """
        now = datetime.now(TZ)
        end = now + timedelta(days=days_ahead)
        events = list_events(now, end)
        if not events:
            return f"Nothing on the calendar in the next {days_ahead} days."

        lines = []
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            lines.append(f"• {e.get('summary', '(no title)')} — {start}")
        return "\n".join(lines)

    @agent.tool_plain
    async def update_meeting(
            event_id: str,
            title: str | None = None,
            start_iso: str | None = None,
            end_iso: str | None = None,
            description: str | None = None,
            location: str | None = None,
    ) -> str:
        """Update an existing calendar event. Provide event_id and any fields to change.

        Args:
            event_id: The event's Google Calendar ID. Get it from list_upcoming_events.
            title: New title (optional).
            start_iso: New start time as ISO 8601 with timezone offset (optional).
            end_iso: New end time as ISO 8601 with timezone offset (optional).
            description: New description (optional).
            location: New location (optional).

        Only the provided fields are changed; others stay the same.
        Use list_upcoming_events first if you don't know the event_id.
        """
        start = None
        if start_iso:
            start = datetime.fromisoformat(start_iso)
            if start.tzinfo is None:
                start = start.replace(tzinfo=TZ)

        end = None
        if end_iso:
            end = datetime.fromisoformat(end_iso)
            if end.tzinfo is None:
                end = end.replace(tzinfo=TZ)

        try:
            link = update_event(event_id, title, start, end, description, location)
        except ValueError as e:
            return str(e)
        return f"Updated event. {link}"

    @agent.tool_plain
    async def cancel_meeting(event_id: str) -> str:
        """Delete a calendar event by ID.

        Args:
            event_id: The event's Google Calendar ID. Get it from list_upcoming_events
                if the user describes the event by time/title rather than ID.
        """
        delete_event(event_id)
        return "Event cancelled."

    