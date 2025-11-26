# app/routers/profile.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.storage.models import User
from app.storage.utils import get_current_user

profile_router = APIRouter(
    prefix="/api",
    tags=["profile"],
)


@profile_router.put("/me")
def update_me(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for field in ("name", "nickname", "profile_pic"):
        if field in data:
            setattr(current_user, field, data[field])
    db.commit()
    db.refresh(current_user)
    return {"result": True}
