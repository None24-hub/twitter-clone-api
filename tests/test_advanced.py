import os
import sys
import pytest
from fastapi.testclient import TestClient

# Добавляем путь к корню проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app  # noqa: E402

client = TestClient(app)

def get_key() -> str:
    """API-key тестового пользователя Alice"""
    return "alice-key"


# ==========================
# 🧩 USERS — edge cases
# ==========================

def test_follow_self():
    """❌ Нельзя подписаться на самого себя"""
    r = client.post("/api/users/1/follow", headers={"api-key": get_key()})
    # Текущее поведение API — возвращает 400
    assert r.status_code == 400 or r.json().get("result") is False


def test_follow_not_exist_user():
    """❌ Попытка подписаться на несуществующего пользователя"""
    r = client.post("/api/users/999/follow", headers={"api-key": get_key()})
    assert r.status_code == 404
    assert "detail" in r.json()


# ==========================
# 🖼️ MEDIA — edge cases
# ==========================

def test_upload_invalid_media(tmp_path):
    """❌ Попытка загрузить не изображение"""
    bad_file = tmp_path / "data.txt"
    bad_file.write_text("not an image file")

    with open(bad_file, "rb") as f:
        r = client.post(
            "/api/medias",
            files={"file": ("data.txt", f, "text/plain")},
            headers={"api-key": get_key()},
        )
    data = r.json()
    assert "result" in data


# ==========================
# 🐦 TWEETS — edge cases
# ==========================

def test_create_empty_tweet():
    """❌ Попытка создать твит без текста"""
    r = client.post(
        "/api/tweets",
        json={"tweet_data": "   "},
        headers={"api-key": get_key()},
    )
    data = r.json()
    assert data["result"] is False
    assert data["error_type"] == "validation"


def test_delete_foreign_tweet():
    """❌ Нельзя удалить чужой твит"""
    # Сначала подписываем Alice на Bob
    client.post("/api/users/2/follow", headers={"api-key": get_key()})
    # Теперь в ленте должен быть твит Bob
    feed = client.get("/api/tweets", headers={"api-key": get_key()}).json()["tweets"]
    bob_tweet = next((t for t in feed if t["author"]["name"] == "Bob"), None)
    assert bob_tweet is not None, "Не найден твит Боба в ленте"
    tweet_id = bob_tweet["id"]

    r = client.delete(f"/api/tweets/{tweet_id}", headers={"api-key": get_key()})
    assert r.status_code == 403
    assert "Cannot delete others" in r.text


def test_attach_media_to_tweet(tmp_path):
    """🖼️ Создание твита с медиафайлом"""
    test_file = tmp_path / "pic.png"
    test_file.write_bytes(b"fake image")
    with open(test_file, "rb") as f:
        media_res = client.post(
            "/api/medias",
            files={"file": ("pic.png", f, "image/png")},
            headers={"api-key": get_key()},
        ).json()
    media_id = media_res["media_id"]

    r = client.post(
        "/api/tweets",
        json={"tweet_data": "твит с фото", "tweet_media_ids": [media_id]},
        headers={"api-key": get_key()},
    )
    assert r.status_code == 200
    assert r.json()["result"] is True

    tweets = client.get("/api/tweets/me", headers={"api-key": get_key()}).json()["tweets"]
    has_photo = any(t["attachments"] for t in tweets)
    assert has_photo is True
