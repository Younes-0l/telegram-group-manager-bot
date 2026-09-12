from database.models.users import User
from database.database import get_session
from sqlalchemy import select, func


def create_user(telegram_id: int, full_name: str, username: str):

    user = User(
        telegram_id=telegram_id,
        full_name=full_name,
        username=username
    )

    with get_session() as session:
        session.add(user)
        session.flush()
        return user

def get_user(telegram_id: int):

    with get_session() as session:

            user = select(User).where(User.telegram_id == telegram_id)
            return session.scalar(user)
        
def create_or_get_user(telegram_id: int, full_name: str, username: str):
    user = get_user(telegram_id)
    if user is None:
        return create_user(telegram_id, full_name, username)

    return user

def create_or_update_user(telegram_id: int, full_name: str, username: str | None):
    with get_session() as session:
        user = session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )

        if user is None:
            user = User(
                telegram_id=telegram_id,
                full_name=full_name,
                username=username
            )
            session.add(user)
        else:
            user.full_name = full_name
            user.username = username

        session.commit()
        session.refresh(user)
        return user

def get_user_by_username(username: str):
    username = username.lstrip("@").lower()
    with get_session() as session:
        stmt = select(User).where(func.lower(User.username) == username)
        return session.scalar(stmt)