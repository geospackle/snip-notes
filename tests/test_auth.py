"""
Tests for authentication endpoints
"""
import pytest


# Signup tests
def test_signup_success(client):
    """Test successful user signup"""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == "newuser@example.com"


def test_signup_invalid_email(client):
    """Test signup with invalid email format"""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "invalid-email",
            "password": "password123"
        }
    )

    assert response.status_code == 422  # Validation error


def test_signup_short_password(client):
    """Test signup with password less than 6 characters"""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "password": "12345"
        }
    )

    assert response.status_code == 400
    assert "at least 6 characters" in response.json()["detail"]


def test_signup_duplicate_email(client):
    """Test signup with already registered email"""
    # First signup
    client.post(
        "/api/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password123"
        }
    )

    # Try to signup again with same email
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "duplicate@example.com",
            "password": "password456"
        }
    )

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_signup_missing_fields(client):
    """Test signup with missing required fields"""
    response = client.post(
        "/api/auth/signup",
        json={"email": "user@example.com"}
    )

    assert response.status_code == 422  # Validation error


# Login tests
def test_login_success(client):
    """Test successful user login"""
    # First create a user
    client.post(
        "/api/auth/signup",
        json={
            "email": "logintest@example.com",
            "password": "password123"
        }
    )

    # Now login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "logintest@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == "logintest@example.com"


def test_login_invalid_email(client):
    """Test login with non-existent email"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_wrong_password(client):
    """Test login with incorrect password"""
    # Create a user
    client.post(
        "/api/auth/signup",
        json={
            "email": "wrongpass@example.com",
            "password": "correctpass"
        }
    )

    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "wrongpass"
        }
    )

    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]


def test_login_missing_fields(client):
    """Test login with missing required fields"""
    response = client.post(
        "/api/auth/login",
        json={"email": "user@example.com"}
    )

    assert response.status_code == 422  # Validation error


# Authentication tests
def test_access_protected_endpoint_with_valid_token(client, authenticated_user):
    """Test accessing protected endpoint with valid token"""
    response = client.get(
        "/api/resources",
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 200


def test_access_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token"""
    response = client.get("/api/resources")

    assert response.status_code == 401  # Unauthorized


def test_access_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token"""
    response = client.get(
        "/api/resources",
        headers={"Authorization": "Bearer invalid-token-here"}
    )

    assert response.status_code == 401  # Unauthorized


def test_access_protected_endpoint_with_malformed_header(client):
    """Test accessing protected endpoint with malformed Authorization header"""
    response = client.get(
        "/api/resources",
        headers={"Authorization": "InvalidFormat token"}
    )

    assert response.status_code == 401  # Unauthorized
