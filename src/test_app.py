"""
Tests for the High School Management System API
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db, User, Activity
from app import app

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create test database and clean up after each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_data():
    """Add sample data to test database"""
    db = TestingSessionLocal()
    
    # Create users
    user1 = User(email="test1@mergington.edu", name="Test User 1")
    user2 = User(email="test2@mergington.edu", name="Test User 2")
    db.add(user1)
    db.add(user2)
    
    # Create activities
    activity1 = Activity(
        name="Test Club",
        description="A test club",
        schedule="Mondays 3:00 PM",
        max_participants=10
    )
    activity2 = Activity(
        name="Test Team",
        description="A test team",
        schedule="Wednesdays 4:00 PM",
        max_participants=5
    )
    
    # Enroll user1 in activity1
    activity1.participants.append(user1)
    
    db.add(activity1)
    db.add(activity2)
    db.commit()
    db.close()


def test_get_activities(client, sample_data):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Test Club" in data
    assert "Test Team" in data
    assert data["Test Club"]["max_participants"] == 10
    assert len(data["Test Club"]["participants"]) == 1


def test_get_user_schedule(client, sample_data):
    """Test getting user's personal schedule"""
    response = client.get("/users/test1@mergington.edu/schedule")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test1@mergington.edu"
    assert len(data["schedule"]) == 1
    assert data["schedule"][0]["name"] == "Test Club"


def test_get_user_schedule_not_found(client):
    """Test getting schedule for non-existent user"""
    response = client.get("/users/nonexistent@mergington.edu/schedule")
    assert response.status_code == 404


def test_login_existing_user(client, sample_data):
    """Test login with existing user"""
    response = client.post("/users/login?email=test1@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test1@mergington.edu"
    assert data["user"]["name"] == "Test User 1"


def test_login_new_user(client, sample_data):
    """Test login creates new user"""
    response = client.post("/users/login?email=newuser@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "newuser@mergington.edu"
    assert data["user"]["name"] == "Newuser"


def test_signup_for_activity(client, sample_data):
    """Test signing up for an activity"""
    response = client.post("/activities/Test Team/signup?email=test2@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up test2@mergington.edu for Test Team" in data["message"]
    
    # Verify enrollment
    schedule_response = client.get("/users/test2@mergington.edu/schedule")
    schedule_data = schedule_response.json()
    assert len(schedule_data["schedule"]) == 1
    assert schedule_data["schedule"][0]["name"] == "Test Team"


def test_signup_already_enrolled(client, sample_data):
    """Test signing up for activity already enrolled in"""
    response = client.post("/activities/Test Club/signup?email=test1@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_signup_activity_not_found(client, sample_data):
    """Test signing up for non-existent activity"""
    response = client.post("/activities/Nonexistent/signup?email=test1@mergington.edu")
    assert response.status_code == 404


def test_signup_activity_full(client, sample_data):
    """Test signing up for full activity"""
    db = TestingSessionLocal()
    activity = db.query(Activity).filter(Activity.name == "Test Team").first()
    
    # Fill up the activity
    for i in range(5):
        user = User(email=f"filler{i}@mergington.edu", name=f"Filler {i}")
        db.add(user)
        activity.participants.append(user)
    db.commit()
    db.close()
    
    # Try to sign up when full
    response = client.post("/activities/Test Team/signup?email=test1@mergington.edu")
    assert response.status_code == 400
    assert "full" in response.json()["detail"]


def test_unregister_from_activity(client, sample_data):
    """Test unregistering from an activity"""
    response = client.delete("/activities/Test Club/unregister?email=test1@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered test1@mergington.edu from Test Club" in data["message"]
    
    # Verify removal
    schedule_response = client.get("/users/test1@mergington.edu/schedule")
    schedule_data = schedule_response.json()
    assert len(schedule_data["schedule"]) == 0


def test_unregister_not_enrolled(client, sample_data):
    """Test unregistering from activity not enrolled in"""
    response = client.delete("/activities/Test Team/unregister?email=test1@mergington.edu")
    assert response.status_code == 400
    assert "not signed up" in response.json()["detail"]


def test_unregister_user_not_found(client, sample_data):
    """Test unregistering non-existent user"""
    response = client.delete("/activities/Test Club/unregister?email=nonexistent@mergington.edu")
    assert response.status_code == 404


def test_unregister_activity_not_found(client, sample_data):
    """Test unregistering from non-existent activity"""
    response = client.delete("/activities/Nonexistent/unregister?email=test1@mergington.edu")
    assert response.status_code == 404
