"""
API Routers for Book Catalog Application

Содержит все маршруты API, сгруппированные по функциональности:
- auth: аутентификация и управление пользователями
- books: CRUD операции и бизнес-логика для книг
- authors: CRUD операции для авторов
- categories: CRUD операции для категорий
"""

from app.routers import auth, books, authors, categories

__all__ = ["auth", "books", "authors", "categories"]