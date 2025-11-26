# storage/media/schemas.py
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    result: bool = False
    error_type: str
    error_message: str


class MediaCreateResponse(BaseModel):
    result: bool = True
    media_id: int


class TweetCreateRequest(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class TweetCreateResponse(BaseModel):
    result: bool = True
    tweet_id: int


class LikeUser(BaseModel):
    user_id: int
    name: str


class AuthorInfo(BaseModel):
    id: int
    name: str


class TweetItem(BaseModel):
    id: int
    content: str
    attachments: List[str]
    author: AuthorInfo
    likes: List[LikeUser]

    class Config:
        orm_mode = True


class TweetFeedResponse(BaseModel):
    result: bool = True
    tweets: List[TweetItem]


class FollowUserShort(BaseModel):
    id: int
    name: str


class UserProfile(BaseModel):
    id: int
    name: str
    followers: List[FollowUserShort]
    following: List[FollowUserShort]

    class Config:
        orm_mode = True


class UserProfileResponse(BaseModel):
    result: bool = True
    user: UserProfile
