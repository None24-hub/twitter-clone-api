# storage/media/models.py
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Table,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# связи follow
followers_table = Table(
    "followers",
    Base.metadata,
    Column("follower_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("following_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("follower_id", "following_id", name="uq_follows_follower_following"),
)

# лайки
likes_table = Table(
    "likes",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("tweet_id", Integer, ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("user_id", "tweet_id", name="uq_likes_user_tweet"),
)

# связь твит–медиа
tweet_medias_table = Table(
    "tweet_medias",
    Base.metadata,
    Column("tweet_id", Integer, ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True),
    Column("media_id", Integer, ForeignKey("medias.id", ondelete="CASCADE"), primary_key=True),
    UniqueConstraint("tweet_id", "media_id", name="uq_tweet_media"),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    # ключ для авторизации
    api_key = Column(String(255), unique=True, nullable=False)

    # дополнительные поля под фронт
    nickname = Column(String(255), nullable=True)
    profile_pic = Column(String(255), nullable=True)

    tweets = relationship("Tweet", back_populates="author", cascade="all, delete-orphan")

    followers = relationship(
        "User",
        secondary=followers_table,
        primaryjoin=id == followers_table.c.following_id,
        secondaryjoin=id == followers_table.c.follower_id,
        backref="following",
    )


class Tweet(Base):
    __tablename__ = "tweets"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("User", back_populates="tweets")

    medias = relationship(
        "Media",
        secondary=tweet_medias_table,
        back_populates="tweets",
    )

    liked_by = relationship(
        "User",
        secondary=likes_table,
        backref="liked_tweets",
    )


class Media(Base):
    __tablename__ = "medias"

    id = Column(Integer, primary_key=True)
    # относительный путь к файлу, который отдадим фронту
    file_path = Column(String(255), nullable=False)

    tweets = relationship(
        "Tweet",
        secondary=tweet_medias_table,
        back_populates="medias",
    )
