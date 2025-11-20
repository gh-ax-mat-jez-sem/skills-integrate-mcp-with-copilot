"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session
from database import get_db, User, Activity

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Get all activities with their participants"""
    activities = db.query(Activity).all()
    
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [user.email for user in activity.participants]
        }
    
    return result


@app.get("/users/{email}/schedule")
def get_user_schedule(email: str, db: Session = Depends(get_db)):
    """Get a specific user's personal schedule"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    schedule = []
    for activity in user.activities:
        schedule.append({
            "name": activity.name,
            "description": activity.description,
            "schedule": activity.schedule
        })
    
    return {
        "user": {
            "email": user.email,
            "name": user.name
        },
        "schedule": schedule
    }


@app.post("/users/login")
def login_user(email: str, db: Session = Depends(get_db)):
    """Login or identify a user by email"""
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        # Create new user if doesn't exist
        name = email.split('@')[0].capitalize()
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    return {
        "user": {
            "email": user.email,
            "name": user.name
        },
        "message": "User authenticated successfully"
    }


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Get or create user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        name = email.split('@')[0].capitalize()
        user = User(email=email, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Get activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if already signed up
    if user in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check if activity is full
    if len(activity.participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is full"
        )
    
    # Add user to activity
    activity.participants.append(user)
    db.commit()
    
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Get user
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get activity
    activity = db.query(Activity).filter(Activity.name == activity_name).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Check if user is signed up
    if user not in activity.participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove user from activity
    activity.participants.remove(user)
    db.commit()
    
    return {"message": f"Unregistered {email} from {activity_name}"}
