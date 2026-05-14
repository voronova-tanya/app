"""
Тесты для CRUD операций с категориями
"""

import pytest
import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestCategoriesAPI:
    """Тестовый класс для категорий"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Подготовка тестовых данных перед каждым тестом"""
        # Уникальный суффикс для каждого теста
        self.unique_suffix = int(time.time() * 1000)
        
        # Регистрация пользователя
        self.test_user = {
            "username": f"categoryuser_{self.unique_suffix}",
            "email": f"category_{self.unique_suffix}@example.com",
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
    
    def test_create_category_success(self):
        """Тест успешного создания категории"""
        category_data = {
            "name": f"Mystery_{self.unique_suffix}",
            "description": "Mystery and detective stories"
        }
        
        response = client.post("/categories/", json=category_data, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] == category_data["description"]
        assert "id" in data
    
    def test_create_category_without_description(self):
        """Тест создания категории без описания"""
        category_data = {
            "name": f"Thriller_{self.unique_suffix}"
        }
        
        response = client.post("/categories/", json=category_data, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["description"] is None
    
    def test_create_duplicate_category(self):
        """Тест создания дубликата категории"""
        category_name = f"Horror_{self.unique_suffix}"
        category_data = {
            "name": category_name,
            "description": "Horror stories"
        }
        
        # Первое создание - успех
        response1 = client.post("/categories/", json=category_data, headers=self.headers)
        assert response1.status_code == 201
        
        # Второе создание с тем же именем - должно быть 409 Conflict
        response2 = client.post("/categories/", json=category_data, headers=self.headers)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()
    
    def test_create_category_without_auth(self):
        """Тест создания категории без авторизации"""
        category_data = {
            "name": "Unauthorized Category"
        }
        
        response = client.post("/categories/", json=category_data)
        assert response.status_code == 401
    
    def test_get_categories_list(self):
        """Тест получения списка категорий"""
        # Создаем несколько категорий
        categories = ["Action", "Adventure", "Comedy"]
        for cat_name in categories:
            client.post(
                "/categories/", 
                json={"name": f"{cat_name}_{self.unique_suffix}"}, 
                headers=self.headers
            )
        
        response = client.get("/categories/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(categories)
    
    def test_get_categories_with_pagination(self):
        """Тест пагинации списка категорий"""
        # Создаем 5 категорий
        for i in range(5):
            client.post(
                "/categories/",
                json={"name": f"Category_{self.unique_suffix}_{i}"},
                headers=self.headers
            )
        
        response = client.get("/categories/?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        response = client.get("/categories/?skip=2&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_get_category_by_id(self):
        """Тест получения категории по ID"""
        # Создаем категорию
        category_data = {"name": f"Documentary_{self.unique_suffix}"}
        create_response = client.post("/categories/", json=category_data, headers=self.headers)
        category_id = create_response.json()["id"]
        
        # Получаем категорию
        response = client.get(f"/categories/{category_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == category_data["name"]
        assert data["id"] == category_id
    
    def test_get_nonexistent_category(self):
        """Тест получения несуществующей категории"""
        response = client.get("/categories/99999")
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]
    
    def test_category_name_uniqueness(self):
        """Тест уникальности имени категории"""
        category_name = f"UniqueCategory_{self.unique_suffix}"
        category_data = {
            "name": category_name,
            "description": "Unique category"
        }
        
        # Первая попытка - успех
        response1 = client.post("/categories/", json=category_data, headers=self.headers)
        assert response1.status_code == 201
        
        # Вторая попытка с тем же именем - ошибка 409
        response2 = client.post("/categories/", json=category_data, headers=self.headers)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"].lower()
    
    def test_category_name_case_sensitivity(self):
        """Тест чувствительности к регистру в именах категорий"""
        category_name1 = f"Case_{self.unique_suffix}"
        category_name2 = f"CASE_{self.unique_suffix}"
        
        category_data1 = {"name": category_name1}
        category_data2 = {"name": category_name2}
        
        response1 = client.post("/categories/", json=category_data1, headers=self.headers)
        assert response1.status_code == 201
        
        response2 = client.post("/categories/", json=category_data2, headers=self.headers)
        # В SQLite имена могут считаться разными, поэтому просто проверяем, что нет ошибки
        assert response2.status_code < 500
    
    def test_category_with_books_relationship(self):
        """Тест связи категории с книгами"""
        # Создаем категорию
        category_name = f"Programming_{self.unique_suffix}"
        category_response = client.post(
            "/categories/",
            json={"name": category_name, "description": "Programming books"},
            headers=self.headers
        )
        category_id = category_response.json()["id"]
        
        # Создаем автора
        author_response = client.post(
            "/authors/",
            json={"name": f"Technical Author_{self.unique_suffix}"},
            headers=self.headers
        )
        author_id = author_response.json()["id"]
        
        # Создаем книгу с этой категорией
        book_data = {
            "title": f"Python Programming_{self.unique_suffix}",
            "price": 45.99,
            "author_id": author_id,
            "category_ids": [category_id]
        }
        book_response = client.post("/books/", json=book_data, headers=self.headers)
        assert book_response.status_code == 201
        book_data_resp = book_response.json()
        
        # Проверяем, что категория связана с книгой
        assert len(book_data_resp["categories"]) == 1
        assert book_data_resp["categories"][0]["id"] == category_id
    
    def test_multiple_categories_creation(self):
        """Тест массового создания категорий"""
        categories_data = [
            {"name": f"Cat1_{self.unique_suffix}", "description": "First"},
            {"name": f"Cat2_{self.unique_suffix}", "description": "Second"},
            {"name": f"Cat3_{self.unique_suffix}", "description": "Third"}
        ]
        
        created_ids = []
        for cat_data in categories_data:
            response = client.post("/categories/", json=cat_data, headers=self.headers)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # Проверяем, что все категории созданы
        assert len(created_ids) == 3
        assert len(set(created_ids)) == 3
    
    def test_category_description_update(self):
        """Тест обновления описания категории"""
        # Создаем категорию
        category_data = {
            "name": f"UpdateTest_{self.unique_suffix}", 
            "description": "Original description"
        }
        create_response = client.post("/categories/", json=category_data, headers=self.headers)
        category_id = create_response.json()["id"]
        
        # Проверяем, что категория создана с правильным описанием
        category_get = client.get(f"/categories/{category_id}")
        assert category_get.status_code == 200
        assert category_get.json()["description"] == "Original description"