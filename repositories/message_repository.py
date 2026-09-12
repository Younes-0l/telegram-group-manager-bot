from database.models.messages import Message
from database.database import get_session
from sqlalchemy import select
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from database.models.users import User
from zoneinfo import ZoneInfo


def save_message(group_id: int, user_id: int, message_id: int):

    message = Message(
        group_id=group_id,
        user_id=user_id,
        message_id=message_id,
    )

    with get_session() as session:
        session.add(message)

    return message

def get_last_messages(group_id: int, limit: int):

    with get_session() as session:

        stmt = (
            select(Message)
            .where(
                Message.group_id == group_id,
                Message.deleted == False
            )
            .order_by(Message.message_id.desc())
            .limit(limit)
        )

        messages = session.scalars(stmt).all()

        return messages

def mark_as_deleted(group_id: int, message_id: int):
    with get_session() as session:
        stmt = select(Message).where(
            Message.group_id == group_id,
            Message.message_id == message_id
        )

        message = session.scalar(stmt)

        if message:
            message.deleted = True

def get_top_users(group_id: int, limit: int) -> str:
    tehran = ZoneInfo("Asia/Tehran")
    today_tehran = datetime.now(tehran).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    today_utc = today_tehran.astimezone(timezone.utc)

    with get_session() as session:

        stmt = (
            select(
                User.full_name,
                func.count(Message.id).label("messages")
            )
            .join(User)
            .where(
                Message.group_id == group_id,
                Message.created_at >= today_utc
            )
            .group_by(User.id)
            .order_by(func.count(Message.id).desc()).limit(limit)
        )
        result = session.execute(stmt).all()
        return result

def today_messages_count(group_id: int) -> int:
    tehran = ZoneInfo("Asia/Tehran")
    today_tehran = datetime.now(tehran).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    today_utc = today_tehran.astimezone(timezone.utc)

    with get_session() as session:
        stmt = (
            select(func.count(Message.id))
            .where(
                Message.group_id == group_id,
                Message.created_at >= today_utc,
            )
        )

        count = session.scalar(stmt)
        return count

def today_deleted_messages_count(group_id: int) -> int:
    tehran = ZoneInfo("Asia/Tehran")
    today_tehran = datetime.now(tehran).replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    today_utc = today_tehran.astimezone(timezone.utc)

    with get_session() as session:
        stmt = (
            select(func.count(Message.id))
            .where(
                Message.group_id == group_id,
                Message.created_at >= today_utc,
                Message.deleted == True,
            )
        )

        count = session.scalar(stmt)
        return count

def yesterday_messages_count(group_id: int) -> int:
    tehran = ZoneInfo("Asia/Tehran")
    today_tehran = datetime.now(tehran).replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = (today_tehran - timedelta(days=1)).astimezone(timezone.utc)
    yesterday_end = today_tehran.astimezone(timezone.utc)

    with get_session() as session:
        stmt = select(func.count(Message.id)).where(
            Message.group_id == group_id,
            Message.created_at >= yesterday_start,
            Message.created_at < yesterday_end
        )
        return session.scalar(stmt) or 0

def get_messages_per_hour(group_id: int) -> dict[int, int]:
    tehran = ZoneInfo("Asia/Tehran")
    today_tehran = datetime.now(tehran).replace(hour=0, minute=0, second=0, microsecond=0)
    today_utc = today_tehran.astimezone(timezone.utc)

    with get_session() as session:
        stmt = select(Message.created_at).where(
            Message.group_id == group_id,
            Message.created_at >= today_utc
        )
        rows = session.scalars(stmt).all()

    hour_counts: dict[int, int] = {}
    for created_at in rows:
        local_hour = created_at.astimezone(tehran).hour
        hour_counts[local_hour] = hour_counts.get(local_hour, 0) + 1

    return hour_counts

def get_busiest_hour(group_id: int) -> tuple[int, int] | None:
    hour_counts = get_messages_per_hour(group_id)
    if not hour_counts:
        return None
    busiest_hour = max(hour_counts, key=hour_counts.get)
    return busiest_hour, hour_counts[busiest_hour]