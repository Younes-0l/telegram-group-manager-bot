from sqlalchemy import String, ForeignKey,UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class BadWord(Base):
    __tablename__ = "bad_words"

    __table_args__ = (
        UniqueConstraint(
            "group_id",
            "word",
            name="uq_group_word",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    group_id: Mapped[int] = mapped_column(
        ForeignKey("groups.id"),
        index=True
    )

    word: Mapped[str] = mapped_column(
        String(100)
    )