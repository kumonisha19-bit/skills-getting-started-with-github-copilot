"""
Tests for the Mergington High School API using Arrange-Act-Assert (AAA) structure.

These tests use `fastapi.testclient.TestClient` so the server does not need to
be running while tests execute.
"""

import copy
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities state for each test."""
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_state)


def generate_unique_email():
    return f"test_user_{uuid4()}@mergington.edu"


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities_response = response.json()
    assert expected_activity_names.issubset(set(activities_response.keys()))
    assert activities_response["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_post_signup_adds_new_participant():
    # Arrange
    email = generate_unique_email()
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert f"Signed up {email}" in response.json()["message"]
    activities_response = client.get("/activities").json()
    assert email in activities_response[activity_name]["participants"]


def test_post_signup_duplicate_returns_400():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_delete_participant_removes_existing_participant():
    # Arrange
    email = generate_unique_email()
    activity_name = "Programming Class"
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    # Act
    delete_response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    # Assert
    assert delete_response.status_code == 200
    assert f"Removed {email}" in delete_response.json()["message"]
    activities_response = client.get("/activities").json()
    assert email not in activities_response[activity_name]["participants"]
