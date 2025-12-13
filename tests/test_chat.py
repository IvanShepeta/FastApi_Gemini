import pytest
from unittest.mock import patch


@pytest.fixture
def mock_gemini():
    """Mock Gemini API calls"""
    with patch("app.routers.post.get_answer_from_gemini") as mock:
        mock.return_value = "This is a mocked response from Gemini"
        yield mock


def test_create_chat_unauthorized(client):
    """Test chat creation without authentication"""
    res = client.post("/chat/", json={"prompt": "Hello"})
    assert res.status_code == 401


def test_create_chat(authorized_client, mock_gemini):
    """Test creating a chat message"""
    res = authorized_client.post(
        "/chat/",
        json={"prompt": "What is FastAPI?"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["prompt"] == "What is FastAPI?"
    assert "response" in data
    assert data["response"] == "This is a mocked response from Gemini"
    assert "id" in data
    assert "created_at" in data
    assert "user_id" in data

    # Verify mock was called
    mock_gemini.assert_called_once_with("What is FastAPI?")


def test_create_chat_empty_prompt(authorized_client):
    """Test chat with empty prompt"""
    res = authorized_client.post("/chat/", json={"prompt": ""})
    assert res.status_code == 422  # Validation error


def test_get_chat_history(authorized_client, test_chats):
    """Test getting chat history"""
    res = authorized_client.get("/chat/history")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2  # test_user has 2 chats
    assert all("prompt" in chat for chat in data)
    assert all("response" in chat for chat in data)
    assert all("id" in chat for chat in data)
    assert all("created_at" in chat for chat in data)


def test_get_chat_history_pagination(authorized_client, test_chats):
    """Test chat history with pagination"""
    res = authorized_client.get("/chat/history?skip=1&limit=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1


def test_get_chat_history_empty(authorized_client):
    """Test getting history when user has no chats"""
    res = authorized_client.get("/chat/history")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 0
    assert isinstance(data, list)


def test_chat_history_isolation(authorized_client, test_chats):
    """Test that users only see their own chats"""
    res = authorized_client.get("/chat/history")
    assert res.status_code == 200
    data = res.json()

    # Should not see test_user2's chat
    prompts = [chat["prompt"] for chat in data]
    assert "Tell me a joke" not in prompts

    # Should only see test_user's chats
    assert "Hello, who are you?" in prompts
    assert "What is Python?" in prompts


def test_chat_history_ordering(authorized_client, test_chats):
    """Test that chat history is ordered by created_at desc"""
    res = authorized_client.get("/chat/history")
    assert res.status_code == 200
    data = res.json()

    # First item should be the most recent
    # Based on test_chats fixture, "What is Python?" is added last
    assert data[0]["prompt"] == "What is Python?"


def test_create_multiple_chats(authorized_client, mock_gemini):
    """Test creating multiple chat messages"""
    prompts = ["Hello", "How are you?", "Tell me about AI"]

    for prompt in prompts:
        res = authorized_client.post("/chat/", json={"prompt": prompt})
        assert res.status_code == 201

    # Check history
    res = authorized_client.get("/chat/history")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
