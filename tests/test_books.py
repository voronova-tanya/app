"""
Тесты для CRUD операций с книгами
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestBooksAPI:
    """Тестовый класс для книг"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Подготовка тестовых данных перед каждым тестом"""
        
        # Уникальное имя пользователя для каждого теста
        unique_suffix = int(time.time() * 1000)
        
        self.test_user = {
            "username": f"bookuser_{unique_suffix}",
            "email": f"bookuser_{unique_suffix}@example.com",
            "password": "testpass123"
        }
        client.post("/auth/register", json=self.test_user)
        
        # Получение токена
        token_response = client.post(
            "/auth/token",
            data={"username": self.test_user["username"], "password": self.test_user["password"]}
        )
        self.token = token_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Создание автора
        author_response = client.post(
            "/authors/",
            json={"name": f"Test Author_{unique_suffix}", "bio": "Test biography"},
            headers=self.headers
        )
        self.author_id = author_response.json()["id"]
        
        # Создание категории с уникальным именем
        category_response = client.post(
            "/categories/",
            json={"name": f"Science Fiction_{unique_suffix}", "description": "Sci-fi books"},
            headers=self.headers
        )
        self.category_id = category_response.json()["id"]
    
    def test_create_book_success(self):
        """Тест успешного создания книги"""
        book_data = {
            "title": "Dune",
            "description": "Classic sci-fi novel",
            "price": 25.99,
            "published_year": 1965,
            "author_id": self.author_id,
            "category_ids": [self.category_id]
        }
        
        response = client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Dune"
        assert data["price"] == 25.99
        assert data["author"]["name"].startswith("Test Author")
    
    def test_create_book_without_author(self):
        """Тест создания книги с несуществующим автором"""
        book_data = {
            "title": "Invalid Book",
            "price": 15.99,
            "author_id": 99999,
            "category_ids": []
        }
        
        response = client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 404
        assert "Author not found" in response.json()["detail"]
    
    def test_create_book_without_auth(self):
        """Тест создания книги без авторизации"""
        book_data = {
            "title": "Unauthorized Book",
            "price": 19.99,
            "author_id": self.author_id
        }
        
        response = client.post("/books/", json=book_data)
        assert response.status_code == 401
    
    def test_get_books_list(self):
        """Тест получения списка книг"""
        # Создаем несколько книг
        for i in range(3):
            book_data = {
                "title": f"Book {i}",
                "price": 10.99 + i,
                "author_id": self.author_id
            }
            client.post("/books/", json=book_data, headers=self.headers)
        
        response = client.get("/books/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_get_book_by_id(self):
        """Тест получения книги по ID"""
        # Создаем книгу
        book_data = {
            "title": "Specific Book",
            "price": 29.99,
            "author_id": self.author_id
        }
        create_response = client.post("/books/", json=book_data, headers=self.headers)
        book_id = create_response.json()["id"]
        
        # Получаем книгу
        response = client.get(f"/books/{book_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Specific Book"
        assert data["views"] >= 1
    
    def test_get_nonexistent_book(self):
        """Тест получения несуществующей книги"""
        response = client.get("/books/99999")
        assert response.status_code == 404
    
    def test_update_book_by_owner(self):
        """Тест обновления книги владельцем"""
        # Создаем книгу
        book_data = {
            "title": "Original Title",
            "price": 19.99,
            "author_id": self.author_id
        }
        create_response = client.post("/books/", json=book_data, headers=self.headers)
        book_id = create_response.json()["id"]
        
        # Обновляем книгу
        update_data = {
            "title": "Updated Title",
            "price": 24.99
        }
        response = client.put(f"/books/{book_id}", json=update_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["price"] == 24.99
    
    def test_update_book_by_non_owner(self):
        """Тест обновления книги другим пользователем"""
        # Создаем книгу первым пользователем
        book_data = {
            "title": "Owner's Book",
            "price": 15.99,
            "author_id": self.author_id
        }
        create_response = client.post("/books/", json=book_data, headers=self.headers)
        book_id = create_response.json()["id"]
        
        # Регистрируем второго пользователя
        unique_suffix = int(time.time() * 1000)
        second_user = {
            "username": f"seconduser_{unique_suffix}",
            "email": f"second_{unique_suffix}@example.com",
            "password": "pass123"
        }
        client.post("/auth/register", json=second_user)
        token_response = client.post(
            "/auth/token",
            data={"username": second_user["username"], "password": second_user["password"]}
        )
        second_token = token_response.json()["access_token"]
        second_headers = {"Authorization": f"Bearer {second_token}"}
        
        # Пытаемся обновить книгу
        update_data = {"title": "Hacked Title"}
        response = client.put(f"/books/{book_id}", json=update_data, headers=second_headers)
        assert response.status_code == 403
    
    def test_delete_book_by_owner(self):
        """Тест удаления книги владельцем"""
        # Создаем книгу
        book_data = {
            "title": "Book to Delete",
            "price": 9.99,
            "author_id": self.author_id
        }
        create_response = client.post("/books/", json=book_data, headers=self.headers)
        book_id = create_response.json()["id"]
        
        # Удаляем книгу
        response = client.delete(f"/books/{book_id}", headers=self.headers)
        assert response.status_code == 204
        
        # Проверяем, что книга удалена
        get_response = client.get(f"/books/{book_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_book(self):
        """Тест удаления несуществующей книги"""
        response = client.delete("/books/99999", headers=self.headers)
        assert response.status_code == 404
    
    def test_create_book_with_invalid_price(self):
        """Тест создания книги с невалидной ценой"""
        book_data = {
            "title": "Invalid Price Book",
            "price": -10.00,
            "author_id": self.author_id
        }
        
        response = client.post("/books/", json=book_data, headers=self.headers)
        assert response.status_code == 422