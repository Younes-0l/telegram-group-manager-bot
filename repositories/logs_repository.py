from database.database import get_session
from database.models.logs import Log, LogAction
from sqlalchemy import select, desc


def add_log(
    action: LogAction,
    group_id: int | None = None,
    actor_id: int | None = None,
    target_id: int | None = None,
    details: str | None = None,
) -> Log:
    with get_session() as session:
        log = Log(
            group_id=group_id,
            action=action.value,
            actor_id=actor_id,
            target_id=target_id,
            details=details,
        )
        session.add(log)
        session.commit()
        session.refresh(log)
        return log


def get_group_logs(group_id: int, limit: int = 20) -> list[Log]:
    with get_session() as session:
        stmt = (
            select(Log)
            .where(Log.group_id == group_id)
            .order_by(desc(Log.created_at))
            .limit(limit)
        )
        return list(session.scalars(stmt).all())


def get_user_logs(group_id: int, target_id: int, limit: int = 20) -> list[Log]:
    with get_session() as session:
        stmt = (
            select(Log)
            .where(Log.group_id == group_id, Log.target_id == target_id)
            .order_by(desc(Log.created_at))
            .limit(limit)
        )
        return list(session.scalars(stmt).all())