# app/storage/media/utils.py
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.storage.models import User


def get_current_user(
    api_key: str = Header(..., alias="api-key"),
    db: Session = Depends(get_db),
) -> User:
    """
    Достаём текущего пользователя по api-key из заголовка.
    Если api-key неверный/нет – кидаем 401.
    """
    user = db.query(User).filter(User.api_key == api_key).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

    return user
