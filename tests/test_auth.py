import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_user():
    
    client.post("/auth/register", json={
        "username": "duplicate",
        "email": "dup@example.com",
        "password": "pass123"
    })
    
    
    response = client.post("/auth/register", json={
        "username": "duplicate",
        "email": "dup2@example.com",
        "password": "pass123"
    })
    assert response.status_code == 400

def test_login():
    
    client.post("/auth/register", json={
        "username": "loginuser",
        "email": "login@example.com",
        "password": "loginpass"
    })
    
    
    response = client.post(
        "/auth/token",
        data={"username": "loginuser", "password": "loginpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"