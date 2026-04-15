import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from core.logging import get_logger

DATABASE_URL = Path("DATABASE_URL")

logger = get_logger(__name__)

def connect() -> sqlite3.Connection:
    '''
    Connection to SQLite
    '''
    conn = sqlite3.connect(DATABASE_URL)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversation (
            user_id TEXT PRIMARY KEY,
            messages TEXT NOT NULL,
            updated_at TIMESTAMP NOT NULL
        )
    """)

    return conn


def load_history(user_id: str) -> list[ModelMessage]:
    '''
    Load the histroy conversation from conversation table
    '''
    with connect() as conn:
        row = conn.execute(
            f"SELECT messages FROM conversation WHERE user_id = ?",
            (user_id, )
        ).fetchone()
    logger.info(f'[SQLITE][LOAD] history loaded')
    if row is None:
        logger.error(f'[SQLITE][LOAD] history return None')
        return []
    return ModelMessagesTypeAdapter.validate_json(row[0])


def save_history(user_id: str, messages: list[ModelMessage]) -> None:
    payload = ModelMessagesTypeAdapter.dump_json(messages).decode()
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            f"""
            INSERT INTO conversation (user_id, messages, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                messages = excluded.messages,
                updated_at = excluded.updated_at
            """,
            (user_id, payload, now)
        )
        logger.info(f'[SQLITE][SAVE] history saved')


def reset_history(user_id: str) -> None:
    '''
    Reset history conversation in case of errors
    '''
    with connect() as conn:
        conn.execute(f"DELETE FROM conversation WHERE user_id = ?", (user_id, ))

    logger.info(f'[SQLITE][RESET] history reset')