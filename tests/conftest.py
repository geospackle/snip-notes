"""
Test fixtures and configuration for pytest
"""
import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.auth.interface import AuthRepository, User


class InMemoryAuthRepository(AuthRepository):
    """In-memory implementation of AuthRepository for testing"""

    def __init__(self):
        self.users = {}

    def create_user(self, email: str, hashed_password: str) -> bool:
        if email in self.users:
            return False
        self.users[email] = User(email=email, hashed_password=hashed_password)
        return True

    def get_user(self, email: str) -> User | None:
        return self.users.get(email)

    def user_exists(self, email: str) -> bool:
        return email in self.users


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables"""
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"


@pytest.fixture
def in_memory_auth_repo():
    """Create an in-memory auth repository for testing"""
    return InMemoryAuthRepository()


@pytest.fixture
def client(in_memory_auth_repo):
    """Create a test client with in-memory dependencies"""
    # Patch the auth repository to use in-memory version
    with patch('src.api.service.auth_repository', in_memory_auth_repo):
        # Import after patching to ensure the patched value is used
        from src.api.service import app

        # Reset the repository for each test
        from src.api.service import repository
        repository._storage.clear()

        # Create test client
        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def mock_analyzers():
    """Mock the AI analyzers to avoid requiring Ollama during tests"""
    mock_web_analyzer = Mock()
    mock_web_analyzer.analyze.return_value = (
        ["technology", "ai", "python"],
        "A test article about AI and Python programming. It covers various topics. Great content."
    )

    mock_text_analyzer = Mock()
    mock_text_analyzer.analyze.return_value = (
        ["note", "idea", "test"],
        "A simple test note. Contains useful information. Good for testing."
    )

    with patch('src.api.service.web_analyzer', mock_web_analyzer), \
         patch('src.api.service.text_analyzer', mock_text_analyzer):
        yield mock_web_analyzer, mock_text_analyzer


@pytest.fixture
def authenticated_user(client):
    """Create a test user and return authentication token"""
    # Sign up a test user
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "test@example.com",
            "password": "testpass123"
        }
    )

    assert signup_response.status_code == 200
    token = signup_response.json()["access_token"]

    return {
        "token": token,
        "email": "test@example.com",
        "headers": {"Authorization": f"Bearer {token}"}
    }


@pytest.fixture
def sample_resources(client, authenticated_user, mock_analyzers):
    """Create sample resources for testing"""
    headers = authenticated_user["headers"]

    # Add a web resource
    web_response = client.post(
        "/api/add",
        json={"content": "https://example.com/article"},
        headers=headers
    )

    # Add a text resource
    text_response = client.post(
        "/api/add",
        json={"content": "This is a test note about programming"},
        headers=headers
    )

    return {
        "web": web_response.json(),
        "text": text_response.json()
    }
