import os
import sys
import pytest
from fastapi.testclient import TestClient

# 🧩 Добавляем путь к корню проекта, чтобы видеть пакет `app`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app  # noqa: E402

client = TestClient(app)


def get_key() -> str:
    """Возвращает api-key для тестового пользователя"""
    return "alice-key"


# ==========================
# 👤 USERS
# ==========================

def test_me():
    """Проверка, что /api/users/me возвращает Alice"""
    r = client.get("/api/users/me", headers={"api-key": get_key()})
    assert r.status_code == 200
    data = r.json()
    assert data["result"] is True
    assert "user" in data
    assert data["user"]["name"] == "Alice"


def test_follow_unfollow():
    """Подписка и отписка от Bob"""
    # Подписка
    r = client.post("/api/users/2/follow", headers={"api-key": get_key()})
    assert r.status_code == 200
    assert r.json()["result"] is True

    # Проверяем, что Bob в списке following
    me = client.get("/api/users/me", headers={"api-key": get_key()}).json()
    following_names = [f["name"] for f in me["user"]["following"]]
    assert "Bob" in following_names

    # Отписка
    r = client.delete("/api/users/2/follow", headers={"api-key": get_key()})
    assert r.status_code == 200
    assert r.json()["result"] is True

    me = client.get("/api/users/me", headers={"api-key": get_key()}).json()
    following_names = [f["name"] for f in me["user"]["following"]]
    assert "Bob" not in following_names


# ==========================
# 🖼️ MEDIA
# ==========================

def test_upload_media(tmp_path):
    """Проверка загрузки медиафайла"""
    test_file = tmp_path / "example.png"
    test_file.write_bytes(b"fake image data")

    with open(test_file, "rb") as f:
        r = client.post(
            "/api/medias",
            files={"file": ("example.png", f, "image/png")},
            headers={"api-key": get_key()},
        )

    assert r.status_code == 200
    data = r.json()
    assert data["result"] is True
    assert "media_id" in data


# ==========================
# 🐦 TWEETS
# ==========================

def test_create_like_delete_tweet():
    """Создание, лайк и удаление твита"""
    # Создаём твит
    r = client.post(
        "/api/tweets",
        json={"tweet_data": "Тестовый твит"},
        headers={"api-key": get_key()},
    )
    assert r.status_code == 200
    assert r.json()["result"] is True

    # Проверяем в /me
    tweets = client.get("/api/tweets/me", headers={"api-key": get_key()}).json()["tweets"]
    assert any(t["content"] == "Тестовый твит" for t in tweets)
    tweet_id = tweets[0]["id"]

    # Лайк
    r = client.post(f"/api/tweets/{tweet_id}/likes", headers={"api-key": get_key()})
    assert r.status_code == 200
    assert r.json()["result"] is True

    # Проверяем, что в ленте есть лайк
    feed = client.get("/api/tweets", headers={"api-key": get_key()}).json()["tweets"]
    liked = any(len(t["likes"]) > 0 for t in feed)
    assert liked is True

    # Удаляем твит
    r = client.delete(f"/api/tweets/{tweet_id}", headers={"api-key": get_key()})
    assert r.status_code == 200
    assert r.json()["result"] is True
