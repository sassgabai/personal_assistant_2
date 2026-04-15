from datetime import datetime
from zoneinfo import ZoneInfo
from pydantic_ai import Agent
from core.logging import get_logger

logger = get_logger(__name__)
TZ = ZoneInfo("Asia/Jerusalem")


def register(agent: Agent) -> None:

    @agent.tool_plain
    async def get_current_datetime() -> str:
        """Get the current date and time in Asia/Jerusalem timezone.

        ALWAYS call this tool BEFORE scheduling anything, setting reminders, or
        resolving any relative time expression like "tomorrow", "next Monday",
        "in 2 hours", "today", "this evening", etc. You cannot determine the
        current date from any other source — you must call this tool.

        Returns the current datetime as ISO 8601 with timezone offset, plus
        the day of the week.
        """
        now = datetime.now(TZ)
        result = f"{now.isoformat()} ({now:%A})"
        logger.info("[DATETIME] returned %s", result)
        return result