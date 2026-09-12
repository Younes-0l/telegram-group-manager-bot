from database.database import get_session
from database.models.mute import Mute
from sqlalchemy import select, func
from datetime import datetime
from .group_members_repository import _get_or_create_member
from zoneinfo import ZoneInfo
from datetime import datetime, timezone


def mute(group_id: int, user_id: int, moderator_id: int, reason: str | None, muted_until: datetime | None):
    with get_session() as session:
        session.execute(
            Mute.__table__.update()
            .where(Mute.group_id == group_id, Mute.user_id == user_id, Mute.is_active == True)
            .values(is_active=False)
        )

        mute = Mute(
            group_id=group_id,
            user_id=user_id,
            moderator_id=moderator_id,
            reason=reason,
            muted_until=muted_until
        )
        session.add(mute)

        member = _get_or_create_member(session, group_id, user_id)
        member.mute_until = muted_until

        session.commit()
        session.refresh(mute)
        return mute

def unmute(group_id: int, user_id: int):
    with get_session() as session:
        session.execute(
            Mute.__table__.update()
            .where(Mute.group_id == group_id, Mute.user_id == user_id, Mute.is_active == True)
            .values(is_active=False)
        )

        member = _get_or_create_member(session, group_id, user_id)
        member.mute_until = None
        session.commit()


def today_mutes_count(group_id: int) -> int:
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
            select(func.count(Mute.id))
            .where(
                Mute.group_id == group_id,
                Mute.created_at >= today_utc,
            )
        )

        count = session.scalar(stmt)
        return count