import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    for activity in activities.values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

def test_signup_activity():
    activity_name = "Chess Club"
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

def test_signup_nonexistent_activity():
    activity_name = "Nonexistent Activity"
    email = "test@example.com"
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 404

def test_unregister_activity():
    # First register a participant
    activity_name = "Chess Club"
    email = "test_unregister@example.com"
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Then unregister them
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]

    # Verify they are no longer in the participants list
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]