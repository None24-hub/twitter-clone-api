from typing import List

from database.database import async_get_db, engine, Base
from fastapi import Depends, HTTPException, status
from models.media import Media
from models.users import User
from models.likes import Like
from models.tweets import Tweet
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_test_user_if_not_exist(session_: AsyncSession):
    query = select(User).where(User.api_key == "test")
    user_query = await session_.execute(query)
    user = user_query.scalar_one_or_none()
    if user is None:
        user = User(api_key="test", username="test user")
        session_.add(user)
        await session_.commit()


async def get_user_by_api_key(
    api_key: str, session: AsyncSession = Depends(async_get_db)
):
    query = (
        select(User)
        .where(User.api_key == api_key)
        .options(
            selectinload(User.following),
            selectinload(User.followers),
        )
    )
    user = await session.execute(query)

    return user.scalar_one_or_none()


async def get_user_by_id(
    user_id: int, session: AsyncSession = Depends(async_get_db)
):
    query = await session.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.following),
            selectinload(User.followers),
        )
    )
    user = query.scalars().one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не существует.",
        )
    return user


async def check_follow_user_ability(
    current_user: User,
    user_being_followed: User,
) -> bool:
    """Проверяем, соответствуют ли следующие запросы всем критериям"""

    if user_being_followed.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to follow yourself",
        )

    elif user_being_followed in current_user.following:
        return False
    return True


async def associate_media_with_tweet(
    tweet: Tweet,
    media_ids: List[int],
    session: AsyncSession = Depends(async_get_db),
):
    """
    Свяжите один или несколько медиаобъектов с твитом.

    Аргументы:
        session (Session): Сеанс SQLAlchemy.
        tweet (Tweet): Объект Tweet для связи с Media.
        media_ids (List[int]): Список идентификаторов медиафайлов, связанных с твитом.
    """
    media_query = await session.execute(
        select(Media).filter(Media.id.in_(media_ids))
    )

    media_objects = media_query.scalars()

    for media in media_objects:
        if not media.tweet_id:
            media.tweet_id = tweet.id

    session.add_all(media_objects)


async def get_media_by_tweet_id(
    tweet_id: int, session: AsyncSession = Depends(async_get_db)
):
    """
    Получаем все медиаобъекты, связанные с твитом.

    Аргументы:
        session (Session): Сеанс SQLAlchemy.
        tweet_id (int): Идентификатор объекта Tweet.
    """
    media_query = await session.execute(
        select(Media).filter(Media.tweet_id == tweet_id)
    )
    media_objects = media_query.scalars().all()
    return media_objects


async def get_tweet_by_id(
    tweet_id: int,
    session: AsyncSession = Depends(async_get_db),
):
    """
    Получите твит по его уникальному идентификатору.

    Параметры:
    - tweet_id (int): уникальный идентификатор твита, который нужно получить.
    - session (AsyncSession, необязательно): асинхронная сессия SQLAlchemy
      (предоставляется функцией `get_db_session`)
      используется для взаимодействия с базой данных.

    Возвращает:
    - Tweet: полученный объект твита.

    Вызывает:
    - HTTPException: если твит с указанным `tweet_id` не найден в базе данных,
      вызывается HTTPException с кодом состояния 404 (не найдено).
    """
    tweet = await session.get(Tweet, tweet_id)

    if not tweet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Твит не был найден!",
        )
    return tweet


async def get_all_following_tweets(session: AsyncSession, current_user: User):
    query = await session.execute(
        select(Tweet)
        .where(
            or_(
                Tweet.user_id.in_(uuid.id for uuid in current_user.following),
                Tweet.user_id == current_user.id,
            )
        )
        .options(
            selectinload(Tweet.user),
            selectinload(Tweet.likes),
            selectinload(Tweet.media),
        )
        .order_by(desc(Tweet.create_date))
    )

    return query.scalars().all()


async def get_all_tweets(session: AsyncSession):
    query = await session.execute(
        select(Tweet)
        .options(
            selectinload(Tweet.user),
            selectinload(Tweet.likes),
            selectinload(Tweet.media),
        )
        .order_by(desc(Tweet.create_date))
    )
    return query.scalars().all()


async def get_like_by_id(session: AsyncSession, tweet_id: int, user_id: int):
    """Получаем лайк по user_id и tweet_id или возвращаем None, если не найдено"""
    query = await session.execute(
        select(Like).where(
            and_(Like.user_id == user_id, Like.tweet_id == tweet_id)
        )
    )
    return query.scalar_one_or_none()
