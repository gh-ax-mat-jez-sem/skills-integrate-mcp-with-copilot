"""
Initialize the database with sample data from the original in-memory storage.
"""

from database import init_db, SessionLocal, User, Activity

# Sample activities from original app
SAMPLE_ACTIVITIES = {
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


def seed_database():
    """Seed the database with initial data"""
    # Initialize database tables
    init_db()

    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(Activity).count() > 0:
            print("Database already contains data. Skipping seed.")
            return

        # Create users from all participant emails
        all_emails = set()
        for activity_data in SAMPLE_ACTIVITIES.values():
            all_emails.update(activity_data["participants"])

        # Create users
        users_map = {}
        for email in all_emails:
            # Extract name from email (e.g., michael@mergington.edu -> Michael)
            name = email.split('@')[0].capitalize()
            user = User(email=email, name=name)
            db.add(user)
            users_map[email] = user

        db.commit()

        # Create activities
        for activity_name, activity_data in SAMPLE_ACTIVITIES.items():
            activity = Activity(
                name=activity_name,
                description=activity_data["description"],
                schedule=activity_data["schedule"],
                max_participants=activity_data["max_participants"]
            )

            # Add participants
            for email in activity_data["participants"]:
                activity.participants.append(users_map[email])

            db.add(activity)

        db.commit()
        print(f"Database seeded successfully with {len(all_emails)} users and {len(SAMPLE_ACTIVITIES)} activities.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
