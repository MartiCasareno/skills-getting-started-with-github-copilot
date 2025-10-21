import pytest
from fastapi.testclient import TestClient
from src.app import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_root(client):
    """Test the root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.is_redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    
    # Verify activity structure
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)

def test_signup_success(client):
    """Test successful activity signup"""
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    
    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate(client):
    """Test signing up same student twice"""
    # First signup
    client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    
    # Try signing up again
    response = client.post("/activities/Chess Club/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"].lower()

def test_signup_nonexistent_activity(client):
    """Test signing up for non-existent activity"""
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()

def test_unregister_success(client):
    """Test successful activity unregistration"""
    # First sign up a student
    email = "unregister@mergington.edu"
    client.post("/activities/Chess Club/signup?email=unregister@mergington.edu")
    
    # Then unregister them
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    
    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_registered(client):
    """Test unregistering a student who isn't registered"""
    response = client.post("/activities/Chess Club/unregister?email=notregistered@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "not registered" in data["detail"].lower()

def test_unregister_nonexistent_activity(client):
    """Test unregistering from non-existent activity"""
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not found" in data["detail"].lower()