from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from ..database import Base
from sqlalchemy.sql import func


class GroupMember(Base):
    __tablename__ = "group_members"

    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id")
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    warnings_count: Mapped[int] = mapped_column(
        default=0
    )

    mute_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    is_banned: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )