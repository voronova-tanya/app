"""
Тесты для Book Catalog Application

Содержит набор автоматических тестов для проверки функциональности API.
"""

import pytest
from fastapi.testclient import TestClient

# Глобальные настройки для тестов
pytest_plugins = []

# Базовые URL для тестирования
BASE_URL = "http://testserver"