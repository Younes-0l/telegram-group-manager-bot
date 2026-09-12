from database.models.whisper import Whisper
from database.database import get_session
from sqlalchemy import select, delete
from datetime import datetime, timedelta, timezone


def create_whisper(sender_id: int, target_id: int, text: str, chat_id: int, message_id: int):
    with get_session() as session:
        whisper = Whisper(
            sender_id=sender_id,
            target_id=target_id,
            text=text,
            chat_id=chat_id,
            message_id=message_id
        )
        session.add(whisper)
        session.commit()
        session.refresh(whisper)
        return whisper


def get_whisper(whisper_id: int):
    with get_session() as session:
        return session.scalar(select(Whisper).where(Whisper.id == whisper_id))


def mark_whisper_read(whisper_id: int):
    with get_session() as session:
        whisper = session.scalar(select(Whisper).where(Whisper.id == whisper_id))
        if whisper:
            whisper.is_read = True
            session.commit()


def delete_old_whispers(hours: int = 24):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    with get_session() as session:
        session.execute(delete(Whisper).where(Whisper.created_at < cutoff))
        session.commit()