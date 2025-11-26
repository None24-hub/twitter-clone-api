from typing import TYPE_CHECKING

from database.database import Base
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .tweets import Tweet


class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True,
    )

    media_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    tweet_id: Mapped[int] = mapped_column(
        ForeignKey("tweets.id"),
        nullable=True,
    )

    # связь с твитом
    tweet: Mapped["Tweet"] = relationship(
        back_populates="media",
    )

    def __repr__(self):
        return self._repr(
            id=self.id,
            media_path=self.media_path,
            tweet_id=self.tweet_id,
        )
