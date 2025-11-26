from datetime import datetime
from typing import TYPE_CHECKING, List

from database.database import Base
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .media import Media
    from .likes import Like
    from .users import User


class Tweet(Base):
    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    create_date: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )

    tweet_data: Mapped[str] = mapped_column(
        String(2500),
        nullable=False,
    )

    # --- связи ---
    user: Mapped["User"] = relationship(back_populates="tweets")

    media: Mapped[List["Media"]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
    )

    likes: Mapped[List["Like"]] = relationship(
        back_populates="tweet",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return self._repr(
            id=self.id,
            user_id=self.user_id,
            create_date=self.create_date,
            tweet_data=self.tweet_data,
        )
