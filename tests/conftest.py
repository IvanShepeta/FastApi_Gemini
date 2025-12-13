from datetime import timedelta, datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.config import settings
from app.main import app
from app.database import get_db, Base
from app.utils import hash as hash_password
from app.oauth2 import create_access_token

SQLALCHEMY_DATABASE_URL = (f"postgresql://{settings.database_username}:{settings.database_password}@"
                           f"{settings.database_hostname}:{settings.database_port}/"
                           f"{settings.database_name}_test")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit= False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def session():
    """Create a fresh database for each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    """Create a test client with overridden database dependency"""
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(session):
    """Create a test user"""
    user_data = {
        "email": "test@example.com",
        "password": hash_password("testpassword123")
    }
    new_user = models.User(**user_data)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@pytest.fixture
def test_user2(session):
    """Create a second test user"""
    user_data = {
        "email": "test2@example.com",
        "password": hash_password("testpassword456")
    }
    new_user = models.User(**user_data)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@pytest.fixture
def test_user_via_api(client):
    """
    Create test user through registration endpoint.
    Use this when you need to test the full registration flow.
    For most tests, use test_user fixture instead (faster).
    """
    user_data = {
        "email": "testtest@email.com",
        "password": "test123123"
    }
    res = client.post("/auth/register", json=user_data)

    assert res.status_code == 201, f"Registration failed: {res.json()}"

    new_user = res.json()
    new_user["password"] = user_data["password"]

    return new_user


def test_login_after_registration(client, test_user_via_api):
    """Test that registered user can login"""
    res = client.post(
        "/auth/login",
        data={
            "username": test_user_via_api["email"],
            "password": test_user_via_api["password"]
        }
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.fixture
def token(test_user):
    """Generate JWT token for test user"""
    return create_access_token({"user_id": test_user.id})


@pytest.fixture
def authorized_client(client, token):
    """Client with authorization header"""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_chats(test_user, test_user2, session):
    """Create test chat messages"""

    base_time = datetime.now(timezone.utc)
    chats_data = [
        {
            "prompt": "Hello, who are you?",
            "response": "I am Gemini AI assistant",
            "user_id": test_user.id,
            "created_at": base_time - timedelta(minutes=2)
        },
        {
            "prompt": "What is Python?",
            "response": "Python is a programming language",
            "user_id": test_user.id,
            "created_at": base_time - timedelta(minutes=1)
        },
        {
            "prompt": "Tell me a joke",
            "response": "Why did the programmer quit? Because they didn't get arrays!",
            "user_id": test_user2.id,
            "created_at": base_time
        }
    ]

    chats = [models.ChatRequest(**chat_data) for chat_data in chats_data]
    session.add_all(chats)
    session.commit()

    for chat in chats:
        session.refresh(chat)

    return chats