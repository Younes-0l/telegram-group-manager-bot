from database.database import get_session
from database.models.member_events import MemberEvent
from sqlalchemy import select, func
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def add_event(group_id: int, user_id: int, event_type: str):
    with get_session() as session:
        event = MemberEvent(group_id=group_id, user_id=user_id, event_type=event_type)
        session.add(event)
        session.commit()


def _today_range_utc():
    tehran = ZoneInfo("Asia/Tehran")
    today_tehran = datetime.now(tehran).replace(hour=0, minute=0, second=0, microsecond=0)
    return today_tehran.astimezone(timezone.utc)


def today_joins_count(group_id: int) -> int:
    today_utc = _today_range_utc()
    with get_session() as session:
        stmt = select(func.count(MemberEvent.id)).where(
            MemberEvent.group_id == group_id,
            MemberEvent.event_type == "joined",
            MemberEvent.created_at >= today_utc
        )
        return session.scalar(stmt) or 0


def today_leaves_count(group_id: int) -> int:
    today_utc = _today_range_utc()
    with get_session() as session:
        stmt = select(func.count(MemberEvent.id)).where(
            MemberEvent.group_id == group_id,
            MemberEvent.event_type == "left",
            MemberEvent.created_at >= today_utc
        )
        return session.scalar(stmt) or 0