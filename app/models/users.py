from typing import List, TYPE_CHECKING

from database.database import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .tweets import Tweet
    from .likes import Like


user_to_user = Table(
    "user_to_user",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True, index=True
    )
    api_key: Mapped[str] = mapped_column(String(255))
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # --- Связь с твитами ---
    tweets: Mapped[List["Tweet"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # --- Связь с лайками ---
    likes: Mapped[List["Like"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # --- Подписки ---
    following: Mapped[List["None"]] = relationship(
        "User",
        secondary=user_to_user,
        primaryjoin=lambda: User.id == user_to_user.c.follower_id,
        secondaryjoin=lambda: User.id == user_to_user.c.following_id,
        backref="followers",
        lazy="selectin",
    )

    def __repr__(self):
        return self._repr(
            id=self.id,
            api_key=self.api_key,
            username=self.username,
        )
