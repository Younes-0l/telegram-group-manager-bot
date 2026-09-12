from ..database import Base
from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from sqlalchemy.sql import func



class Message(Base):
    __tablename__ = "messages"

    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "message_id",
            name="uq_group_message",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    message_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    server_default=func.now()
    )

    deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )