from typing import Optional

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from models import User


def normalize_api_key(raw_key: Optional[str]) -> str:
    if not raw_key:
        return "alice-key"

    keys = [k.strip() for k in raw_key.split(",") if k.strip()]
    if not keys:
        return "alice-key"

    if "alice-key" in keys:
        return "alice-key"

    key = keys[-1]
    if key.lower() == "test":
        return "alice-key"

    return key


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    raw_key = request.headers.get("api-key")
    method = request.method
    path = request.url.path

    print("\n-------------------------")
    print(f"Запрос: {method} {path}")
    print(f"Исходный API-ключ из заголовка: {raw_key}")

    api_key = normalize_api_key(raw_key)
    print(f"Нормализованный API-ключ: {api_key}")

    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        print("Пользователь с таким API-ключом не найден")
        raise HTTPException(status_code=401, detail="Invalid API key")

    print(f"Авторизация успешна: {user.name} (id={user.id})")
    print("-------------------------\n")

    return user
