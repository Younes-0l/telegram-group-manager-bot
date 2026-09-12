from database.database import get_session
from database.models.warnings import Warning
from sqlalchemy import select, func
from .group_members_repository import _get_or_create_member
from zoneinfo import ZoneInfo
from datetime import datetime, timezone


def add_warn(group_id: int, user_id: int, moderator_id: int, reason: str | None) -> int:

    with get_session() as session:
        warning = Warning(
            group_id=group_id,
            user_id=user_id,
            moderator_id=moderator_id,
            reason=reason
        )
        session.add(warning)

        member = _get_or_create_member(session, group_id, user_id)
        member.warnings_count += 1

        session.commit()
        session.refresh(warning)
        return warning, member.warnings_count

def remove_last_warning(group_id: int, user_id: int) -> int:

    with get_session() as session:
        last_warning = session.scalar(
            select(Warning)
            .where(
                Warning.group_id == group_id,
                Warning.user_id == user_id,
                Warning.is_active == True
            )
            .order_by(Warning.created_at.desc())
        )

        if last_warning is not None:
            last_warning.is_active = False

        member = _get_or_create_member(session, group_id, user_id)

        member.warnings_count = max(member.warnings_count - 1, 0)

        session.commit()
        session.refresh(member)
        return member.warnings_count


def clear_warns(group_id: int, user_id: int):

    with get_session() as session:
        session.execute(
            Warning.__table__.update()
            .where(Warning.group_id == group_id, Warning.user_id == user_id)
            .values(is_active=False)
        )

        member = _get_or_create_member(session, group_id, user_id)
        member.warnings_count = 0    
        session.commit()

def get_warn_count(group_id: int, user_id: int) -> int:

    with get_session() as session:
        member = _get_or_create_member(session, group_id, user_id)
        return member.warnings_count
    
def get_active_warnings_count(group_id: int, user_id: int) -> int:
    with get_session() as session:
        stmt = select(Warning).where(
            Warning.group_id == group_id,
            Warning.user_id == user_id,
            Warning.is_active == True
        )
        return session.scalars(stmt).all() or None

def today_warnings_count(group_id: int) -> int:
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
            select(func.count(Warning.id))
            .where(
                Warning.group_id == group_id,
                Warning.created_at >= today_utc,
            )
        )

        count = session.scalar(stmt)
        return count