from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.database import get_session
from database.models.group_members import GroupMember
from database.models.groups import Group
from database.models.users import User

def _get_or_create_member(
    session: Session,
    group_id: int,
    user_id: int,
) -> GroupMember:

    member = session.scalar(
        select(GroupMember).where(
            GroupMember.group_id == group_id,
            GroupMember.user_id == user_id,
        )
    )

    if member is None:
        member = GroupMember(
            group_id=group_id,
            user_id=user_id,
            warnings_count=0,
        )
        session.add(member)
        session.flush()

    if member.mute_until and member.mute_until <= datetime.now(timezone.utc):
        member.mute_until = None

    return member

def resolve_ids(chat_id: int, telegram_user_id: int) -> tuple[int, int]:
    with get_session() as session:
        group = session.scalar(select(Group).where(Group.chat_id == chat_id))
        user = session.scalar(select(User).where(User.telegram_id == telegram_user_id))
        return group, user