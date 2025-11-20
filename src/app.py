"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Admin configuration
ADMIN_IDS = os.getenv("ADMIN_IDS", "").split(",")
ADMIN_IDS = [admin_id.strip() for admin_id in ADMIN_IDS if admin_id.strip()]


# Pydantic models
class ActivityCreate(BaseModel):
    name: str
    description: str
    schedule: str
    max_participants: int


# Admin authentication helper
def verify_admin(user_id: Optional[str] = Header(None, alias="X-User-ID")):
    """Verify if the user is an admin"""
    if not user_id or user_id not in ADMIN_IDS:
        raise HTTPException(status_code=403, detail="Forbidden: Admin access required")
    return user_id

# In-memory activity database
activities = {
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
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}


# Admin endpoints
@app.get("/admin/stats")
def get_admin_stats(admin_id: str = Header(None, alias="X-User-ID")):
    """Get system statistics (admin only)"""
    verify_admin(admin_id)
    
    # Calculate statistics
    all_students = set()
    total_enrollments = 0
    total_capacity = 0
    total_enrolled = 0
    
    for activity in activities.values():
        all_students.update(activity["participants"])
        total_enrollments += len(activity["participants"])
        total_capacity += activity["max_participants"]
        total_enrolled += len(activity["participants"])
    
    capacity_utilization = (total_enrolled / total_capacity * 100) if total_capacity > 0 else 0
    
    return {
        "total_students": len(all_students),
        "total_activities": len(activities),
        "total_enrollments": total_enrollments,
        "capacity_utilization": round(capacity_utilization, 2),
        "total_capacity": total_capacity,
        "total_enrolled": total_enrolled
    }


@app.get("/admin/users")
def get_all_users(admin_id: str = Header(None, alias="X-User-ID")):
    """Get all registered users (admin only)"""
    verify_admin(admin_id)
    
    # Collect all unique users
    all_students = set()
    user_activity_map = {}
    
    for activity_name, activity in activities.items():
        for email in activity["participants"]:
            all_students.add(email)
            if email not in user_activity_map:
                user_activity_map[email] = []
            user_activity_map[email].append(activity_name)
    
    # Format users with their activities
    users = [
        {
            "email": email,
            "activities": user_activity_map[email],
            "activity_count": len(user_activity_map[email])
        }
        for email in sorted(all_students)
    ]
    
    return {"users": users, "total": len(users)}


@app.get("/admin/activities/popular")
def get_popular_activities(admin_id: str = Header(None, alias="X-User-ID")):
    """Get most popular activities by enrollment (admin only)"""
    verify_admin(admin_id)
    
    # Calculate popularity
    activity_stats = []
    for name, details in activities.items():
        enrollment_count = len(details["participants"])
        capacity = details["max_participants"]
        utilization = (enrollment_count / capacity * 100) if capacity > 0 else 0
        
        activity_stats.append({
            "name": name,
            "enrollment": enrollment_count,
            "capacity": capacity,
            "utilization": round(utilization, 2),
            "schedule": details["schedule"]
        })
    
    # Sort by enrollment (descending)
    activity_stats.sort(key=lambda x: x["enrollment"], reverse=True)
    
    return {"activities": activity_stats}


@app.post("/admin/activities")
def create_activity(activity: ActivityCreate, admin_id: str = Header(None, alias="X-User-ID")):
    """Create a new activity (admin only)"""
    verify_admin(admin_id)
    
    # Check if activity already exists
    if activity.name in activities:
        raise HTTPException(status_code=400, detail="Activity already exists")
    
    # Create the activity
    activities[activity.name] = {
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "participants": []
    }
    
    return {"message": f"Activity '{activity.name}' created successfully", "activity": activity.name}


@app.delete("/admin/activities/{activity_name}")
def delete_activity(activity_name: str, admin_id: str = Header(None, alias="X-User-ID")):
    """Delete an activity (admin only)"""
    verify_admin(admin_id)
    
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    del activities[activity_name]
    return {"message": f"Activity '{activity_name}' deleted successfully"}


@app.put("/admin/activities/{activity_name}")
def update_activity(activity_name: str, activity: ActivityCreate, admin_id: str = Header(None, alias="X-User-ID")):
    """Update an existing activity (admin only)"""
    verify_admin(admin_id)
    
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Keep existing participants
    existing_participants = activities[activity_name]["participants"]
    
    # Update activity with new data
    activities[activity_name] = {
        "description": activity.description,
        "schedule": activity.schedule,
        "max_participants": activity.max_participants,
        "participants": existing_participants
    }
    
    return {"message": f"Activity '{activity_name}' updated successfully"}
