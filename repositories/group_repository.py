from database.models.groups import Group
from database.database import get_session
from sqlalchemy import select
from sqlalchemy.orm import Session


def create_or_get_group(chat_id: int, title: str):

    with get_session() as session:

        group = session.scalar(
            select(Group).where(
                Group.chat_id == chat_id
            )
        )

        if group is None:
            group = Group(
                chat_id=chat_id,
                title=title
            )
            session.add(group)
            session.flush()

        return group

def _get_or_create_group(
    session: Session,
    chat_id: int,
    title: str,
) -> Group:

    group = session.scalar(
        select(Group).where(
            Group.chat_id == chat_id
        )
    )

    if group is None:
        group = Group(
            chat_id=chat_id,
            title=title
        )
        session.add(group)
        session.flush()

    return group

def set_rules(chat_id: int, title: str, rules: str) -> None:

    with get_session() as session:
        group = _get_or_create_group(session, chat_id, title)
        group.rules = rules

def delete_rules(chat_id: int, title: str) -> bool:

    with get_session() as session:
        group = _get_or_create_group(session, chat_id, title)
        if group.rules is None:
            return False
        
        group.rules = None
        return True

def get_rules(chat_id: int, title: str) -> str:

    with get_session() as session:
        group = _get_or_create_group(session, chat_id, title)
        return group.rules