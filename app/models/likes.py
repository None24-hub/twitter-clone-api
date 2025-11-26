from typing import TYPE_CHECKING

from database.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .users import User
    from .tweets import Tweet


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweets.id"),
        nullable=False
    )

    # связи
    user: Mapped["User"] = relationship(back_populates="likes")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")

    def __repr__(self):
        return self._repr(
            id=self.id,
            user_id=self.user_id,
            tweet_id=self.tweet_id,
        )
