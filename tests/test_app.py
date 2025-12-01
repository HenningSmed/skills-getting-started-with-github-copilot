"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities

# Create test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
    }
    
    # Clear current activities
    activities.clear()
    
    # Populate with test data
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_returns_activity_details(self):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert activity["description"]
        assert activity["schedule"]
        assert activity["max_participants"] == 12
        assert "participants" in activity
        assert len(activity["participants"]) == 2


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=john@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "john@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_for_nonexistent_activity(self):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Fake%20Club/signup?email=john@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_registered(self):
        """Test signup fails when student is already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_multiple_students(self):
        """Test multiple students can sign up for the same activity"""
        client.post("/activities/Chess%20Club/signup?email=alice@mergington.edu")
        response = client.post(
            "/activities/Chess%20Club/signup?email=bob@mergington.edu"
        )
        
        assert response.status_code == 200
        assert len(activities["Chess Club"]["participants"]) == 4
        assert "alice@mergington.edu" in activities["Chess Club"]["participants"]
        assert "bob@mergington.edu" in activities["Chess Club"]["participants"]


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_unregister_successful(self):
        """Test successful unregistration of a participant"""
        response = client.delete(
            "/activities/Chess%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self):
        """Test unregister fails for nonexistent activity"""
        response = client.delete(
            "/activities/Fake%20Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_nonexistent_participant(self):
        """Test unregister fails when participant not in activity"""
        response = client.delete(
            "/activities/Chess%20Club/participants/notregistered@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_unregister_reduces_participant_count(self):
        """Test that unregistering reduces the participant count"""
        initial_count = len(activities["Chess Club"]["participants"])
        client.delete("/activities/Chess%20Club/participants/michael@mergington.edu")
        final_count = len(activities["Chess Club"]["participants"])
        
        assert final_count == initial_count - 1


class TestRoot:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_index(self):
        """Test that root path redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
