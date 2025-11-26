from typing import Annotated

from aiofiles import os as aiofiles_os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from database.database import async_get_db
from database.utils import (
    associate_media_with_tweet,
    get_all_following_tweets,
    get_like_by_id,
    get_media_by_tweet_id,
    get_tweet_by_id,
    get_user_by_id,
)
from models.likes import Like
from models.tweets import Tweet
from models.users import User
from schemas.base_schema import DefaultSchema
from schemas.tweet_schema import TweetIn
from utils.auth import authenticate_user
from utils.settings import MEDIA_PATH

router = APIRouter(prefix="/api", tags=["tweets_and_likes_v1"])


@router.post(
    "/tweets",
    status_code=status.HTTP_201_CREATED,
)
async def create_tweet(
    tweet_in: TweetIn,
    current_user: Annotated[
        User, "User model obtained from the api key"
    ] = Depends(authenticate_user),
    session: AsyncSession = Depends(async_get_db),
):
    """Создать твит"""
    new_tweet = Tweet(
        user_id=current_user.id,
        tweet_data=tweet_in.tweet_data,
    )
    session.add(new_tweet)
    await session.flush()  # чтобы у new_tweet уже был id

    tweet_media_ids = tweet_in.tweet_media_ids
    if tweet_media_ids:
        await associate_media_with_tweet(
            session=session, media_ids=tweet_media_ids, tweet=new_tweet
        )

    await session.commit()

    return {"result": True, "tweet_id": new_tweet.id}


@router.delete(
    "/tweets/{tweet_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_tweet(
    tweet_id: int,
    current_user: Annotated[
        User, "User model obtained from the api key"
    ] = Depends(authenticate_user),
    session: AsyncSession = Depends(async_get_db),
):
    tweet_to_delete = await get_tweet_by_id(tweet_id, session)
    if tweet_to_delete is None:
        # структура как в тестах (error_response)
        error_body = {
            "result": False,
            "error_type": "Not Found",
            "error_message": "Твит не был найден!",
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_body,
        )

    if tweet_to_delete.user_id != current_user.id:
        error_body = {
            "result": False,
            "error_type": "Forbidden",
            "error_message": "К сожалению, вы не можете удалить твиты, созданные другим пользователем.",
        }
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_body,
        )

    media_to_delete = await get_media_by_tweet_id(tweet_id, session)
    for media in media_to_delete:
        path_to_delete = MEDIA_PATH / media.media_path
        await aiofiles_os.remove(path_to_delete)

    await session.delete(tweet_to_delete)
    await session.commit()

    return {"result": True}


@router.post(
    "/tweets/{tweet_id}/likes",
    status_code=status.HTTP_201_CREATED,
    response_model=DefaultSchema,
)
async def like_a_tweet(
    tweet_id: int,
    current_user: Annotated[
        User, "User model obtained from the api key"
    ] = Depends(authenticate_user),
    session: AsyncSession = Depends(async_get_db),
):
    """Поставить лайк твиту"""
    tweet_to_like = await get_tweet_by_id(tweet_id=tweet_id, session=session)
    if tweet_to_like is None:
        # используется в test_like_tweet_that_doesnt_exist
        error_body = {
            "result": False,
            "error_type": "Not Found",
            "error_message": "Твит не был найден!",
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_body,
        )

    # уже лайкал? — идемпотентность
    like = await get_like_by_id(
        session=session, tweet_id=tweet_id, user_id=current_user.id
    )
    if like:
        return {"result": True}

    # нельзя лайкать свой твит
    if tweet_to_like.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя лайкать собственный твит.",
        )

    like_to_add = Like(user_id=current_user.id, tweet_id=tweet_to_like.id)
    session.add(like_to_add)
    await session.commit()

    return {"result": True}


@router.delete(
    "/tweets/{tweet_id}/likes",
    status_code=status.HTTP_200_OK,
)
async def delete_like_from_tweet(
    tweet_id: int,
    current_user: Annotated[
        User, "User model obtained from the api key"
    ] = Depends(authenticate_user),
    session: AsyncSession = Depends(async_get_db),
):
    tweet = await get_tweet_by_id(tweet_id=tweet_id, session=session)
    if tweet is None:
        error_body = {
            "result": False,
            "error_type": "Not Found",
            "error_message": "Tweet was not found!",
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_body,
        )

    like = await get_like_by_id(
        session=session, tweet_id=tweet.id, user_id=current_user.id
    )

    if like is None:
        # именно это сообщение ожидает test_delete_tweet_like_from_different_user
        error_body = {
            "result": False,
            "error_type": "Not Found",
            "error_message": "Вы и так не лайкаете этот твит.",
        }
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_body,
        )

    await session.delete(like)
    await session.commit()

    return {"result": True}


@router.get("/tweets", status_code=status.HTTP_200_OK)
async def get_tweets(
    current_user: Annotated[
        User, "User model obtained from the api key"
    ] = Depends(authenticate_user),
    session: AsyncSession = Depends(async_get_db),
):
    """
    Получить ленту твитов (текущий пользователь + те, на кого он подписан),
    с медиой и лайками, отсортированную по количеству лайков.
    """
    all_tweets = await get_all_following_tweets(
        session=session,
        current_user=current_user,
    )

    if not all_tweets:
        answer = {"result": True, "tweets": []}
        return JSONResponse(content=answer, status_code=200)

    all_following_tweets = []

    for tweet in all_tweets:
        single_tweet = {
            "id": tweet.id,
            "content": tweet.tweet_data,
        }

        # вложения
        single_tweet["attachments"] = [
            media.media_path for media in tweet.media
        ]

        # автор
        tweet_author = await get_user_by_id(tweet.user_id, session)
        single_tweet["author"] = {
            "id": tweet.user_id,
            "name": tweet_author.username,
        }

        # лайки
        single_tweet_likes = []
        for like in tweet.likes:
            liker = await get_user_by_id(like.user_id, session)
            single_tweet_likes.append(
                {"user_id": like.user_id, "name": liker.username}
            )

        single_tweet["likes"] = single_tweet_likes
        all_following_tweets.append(single_tweet)

    # сортировка по количеству лайков (по убыванию)
    all_following_tweets.sort(key=lambda t: len(t["likes"]), reverse=True)

    answer = {
        "result": True,
        "tweets": all_following_tweets,
    }

    return JSONResponse(content=answer, status_code=200)


@router.get("/tweets/{user_id}", status_code=status.HTTP_200_OK)
async def get_following_tweets(
    user_id: int,
    current_user: Annotated[
        User, "User model obtained from the api key"
    ] = Depends(authenticate_user),
    session: AsyncSession = Depends(async_get_db),
):
    """
    Получить твиты для указанного пользователя (по его id).
    """
    user = await get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    all_tweets = await get_all_following_tweets(
        session=session,
        current_user=user,
    )

    return {"result": True, "tweets": [t.id for t in all_tweets]}
