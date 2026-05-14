import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def setup_test_data():
    """Создание уникальных тестовых данных"""
    unique_suffix = int(time.time() * 1000)
    
    # Регистрация пользователя с уникальным именем
    username = f"business_user_{unique_suffix}"
    email = f"business_{unique_suffix}@example.com"
    
    client.post("/auth/register", json={
        "username": username,
        "email": email,
        "password": "testpass"
    })
    
    # Получение токена
    token_resp = client.post("/auth/token", data={
        "username": username,
        "password": "testpass"
    })
    token = token_resp.json()["access_token"]
    
    # Создание автора с уникальным именем
    author_resp = client.post(
        "/authors/",
        json={"name": f"Test Author_{unique_suffix}", "bio": "Test bio"},
        headers={"Authorization": f"Bearer {token}"}
    )
    author_id = author_resp.json()["id"]
    
    # Создание категории с уникальным именем
    category_resp = client.post(
        "/categories/",
        json={"name": f"Fiction_{unique_suffix}", "description": "Fiction books"},
        headers={"Authorization": f"Bearer {token}"}
    )
    category_id = category_resp.json()["id"]
    
    # Создание книги
    book_resp = client.post(
        "/books/",
        json={
            "title": f"Test Book_{unique_suffix}",
            "price": 29.99,
            "author_id": author_id,
            "category_ids": [category_id]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    book_id = book_resp.json()["id"]
    
    return token, book_id, author_id, category_id


def test_rate_book():
    """Тест оценки книги"""
    token, book_id, _, _ = setup_test_data()
    
    response = client.post(
        f"/books/{book_id}/rate",
        json={"user_rating": 4.5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == book_id
    assert "recommendation" in data
    assert data["new_rating"] > 0


def test_get_similar_books():
    """Тест получения похожих книг"""
    token, book_id, author_id, category_id = setup_test_data()
    
    # Создаем еще одну книгу для сравнения с уникальным названием
    unique_suffix = int(time.time() * 1000)
    client.post(
        "/books/",
        json={
            "title": f"Another Book_{unique_suffix}",
            "price": 19.99,
            "author_id": author_id,
            "category_ids": [category_id]
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    response = client.get(f"/books/{book_id}/similar?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "match_score" in data[0]
        assert "reasons" in data[0]


def test_top_rated_books():
    """Тест получения топ книг"""
    response = client.get("/books/top/rated?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)