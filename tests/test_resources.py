"""
Tests for resource management endpoints
"""
import pytest


# Add resource tests
def test_add_web_resource_success(client, authenticated_user, mock_analyzers):
    """Test successfully adding a web resource"""
    response = client.post(
        "/api/add",
        json={"content": "https://example.com/article"},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "https://example.com/article"
    assert data["resource_type"] == "web"
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) > 0
    assert data["description"] != ""


def test_add_text_resource_success(client, authenticated_user, mock_analyzers):
    """Test successfully adding a text resource"""
    response = client.post(
        "/api/add",
        json={"content": "This is my note about Python programming"},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["content"] == "This is my note about Python programming"
    assert data["resource_type"] == "text"
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) > 0
    assert data["description"] != ""


def test_add_resource_with_custom_tags_and_description(client, authenticated_user):
    """Test adding a resource with custom tags and description"""
    custom_tags = ["custom", "tag", "test"]
    custom_desc = "This is a custom description."

    response = client.post(
        "/api/add",
        json={
            "content": "https://example.com",
            "tags": custom_tags,
            "description": custom_desc,
        },
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert data["tags"] == custom_tags
    assert data["description"] == custom_desc


def test_add_resource_empty_content(client, authenticated_user):
    """Test adding a resource with empty content"""
    response = client.post(
        "/api/add",
        json={"content": "   "},
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_add_resource_without_authentication(client):
    """Test adding a resource without authentication"""
    response = client.post(
        "/api/add",
        json={"content": "https://example.com"}
    )

    assert response.status_code == 401


def test_add_resource_missing_content(client, authenticated_user):
    """Test adding a resource without content field"""
    response = client.post(
        "/api/add",
        json={},
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 422  # Validation error


# Search resources tests
def test_search_by_tag_success(client, authenticated_user, sample_resources):
    """Test successfully searching resources by tag"""
    # Search for a tag that exists
    response = client.post(
        "/api/search",
        json={"tag": "technology"},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Verify the tag exists in at least one result
    assert any("technology" in resource["tags"] for resource in data)


def test_search_by_tag_no_results(client, authenticated_user, sample_resources):
    """Test searching for a tag that doesn't exist"""
    response = client.post(
        "/api/search",
        json={"tag": "nonexistent"},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_search_by_tag_case_insensitive(client, authenticated_user, sample_resources):
    """Test that tag search is case insensitive"""
    # Search with different cases
    response1 = client.post(
        "/api/search",
        json={"tag": "TECHNOLOGY"},
        headers=authenticated_user["headers"],
    )
    response2 = client.post(
        "/api/search",
        json={"tag": "technology"},
        headers=authenticated_user["headers"],
    )

    assert response1.status_code == 200
    assert response2.status_code == 200
    # Both should return same results
    assert len(response1.json()) == len(response2.json())


def test_search_empty_tag(client, authenticated_user):
    """Test searching with empty tag"""
    response = client.post(
        "/api/search",
        json={"tag": "   "},
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_search_without_authentication(client):
    """Test searching without authentication"""
    response = client.post(
        "/api/search",
        json={"tag": "test"}
    )

    assert response.status_code == 401


def test_search_missing_tag(client, authenticated_user):
    """Test searching without tag field"""
    response = client.post(
        "/api/search",
        json={},
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 422  # Validation error


# Get all resources tests
def test_get_all_resources_success(client, authenticated_user, sample_resources):
    """Test successfully getting all resources"""
    response = client.get(
        "/api/resources",
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2  # We added 2 sample resources


def test_get_all_resources_empty(client, authenticated_user):
    """Test getting all resources when none exist"""
    response = client.get(
        "/api/resources",
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_all_resources_without_authentication(client):
    """Test getting all resources without authentication"""
    response = client.get("/api/resources")

    assert response.status_code == 401


def test_get_all_resources_structure(client, authenticated_user, sample_resources):
    """Test that all resources have the correct structure"""
    response = client.get(
        "/api/resources",
        headers=authenticated_user["headers"]
    )

    assert response.status_code == 200
    data = response.json()

    for resource in data:
        assert "id" in resource
        assert "content" in resource
        assert "resource_type" in resource
        assert "tags" in resource
        assert "description" in resource
        assert resource["resource_type"] in ["web", "text"]
        assert isinstance(resource["tags"], list)


# Health check tests
def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_health_check_no_auth_required(client):
    """Test that health check doesn't require authentication"""
    response = client.get("/health")

    assert response.status_code == 200
