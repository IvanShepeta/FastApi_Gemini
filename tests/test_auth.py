import pytest
from jose import jwt


def test_root(client):
    """Test root endpoint"""
    res = client.get("/")
    assert res.status_code == 200
    assert res.json() == {"message": "Hello World"}

def test_create_user(client):
    """Test user registration"""
    res = client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "password123"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "created_at" in data