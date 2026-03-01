import copy
import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def client():
    """Provide a TestClient and ensure activities reset before each test."""
    # Arrange: reset to known initial state
    app_module.reset_activities()
    client = TestClient(app_module.app)
    yield client


def test_root_redirect(client):
    # Arrange: nothing to prepare (fixture already resets)

    # Act - do not follow the redirect so we can assert on its details
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities(client):
    # Arrange: initial state contains Chess Club

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"], dict)


def test_signup_success(client):
    # Arrange
    email = "tester@mergington.edu"
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json().get("message", "")
    # verify change persisted
    all_acts = client.get("/activities").json()
    assert email in all_acts[activity]["participants"]


def test_signup_duplicate(client):
    # Arrange
    email = "michael@mergington.edu"  # already in Chess Club
    activity = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json().get("detail", "")


def test_signup_not_found(client):
    # Arrange
    email = "ghost@mergington.edu"
    activity = "Nonexistent"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404


def test_remove_signup_success(client):
    # Arrange
    email = "daniel@mergington.edu"
    activity = "Chess Club"

    # Act
    resp = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")
    remaining = client.get("/activities").json()
    assert email not in remaining[activity]["participants"]


def test_remove_signup_not_signed_up(client):
    # Arrange
    email = "nobody@mergington.edu"
    activity = "Chess Club"

    # Act
    resp = client.delete(f"/activities/{activity}/signup?email={email}")

    # Assert
    assert resp.status_code == 400

