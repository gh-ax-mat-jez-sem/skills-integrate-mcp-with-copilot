# High School Management System - Setup Guide

## Overview
This application manages extracurricular activities for Mergington High School with individual student schedules stored in PostgreSQL database.

## Prerequisites
- Python 3.12+
- PostgreSQL 16+
- pip (Python package manager)

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up PostgreSQL Database

**Start PostgreSQL service:**
```bash
sudo systemctl start postgresql
```

**Create the database:**
```bash
sudo -u postgres psql -c "CREATE DATABASE school_management;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'postgres';"
```

**Configure database connection:**
Create a `.env` file in the root directory:
```
DATABASE_URL=postgresql://postgres:postgres@localhost/school_management
```

### 3. Initialize Database with Sample Data
```bash
cd src
python3 init_db.py
```

## Running the Application

### Start the Server
```bash
cd src
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
```

The application will be available at: http://localhost:8000

## Running Tests

```bash
cd src
python3 -m pytest test_app.py -v
```

All 13 tests should pass.

## Features

### For Students:
- **Login**: Authenticate with your school email
- **View Personal Schedule**: See all activities you're enrolled in
- **Browse Activities**: View all available extracurricular activities
- **Sign Up**: Enroll in activities with available spots
- **Unregister**: Remove yourself from activities

### API Endpoints:

- `GET /activities` - List all activities with participants
- `GET /users/{email}/schedule` - Get a student's personal schedule
- `POST /users/login?email={email}` - Login/authenticate a user
- `POST /activities/{name}/signup?email={email}` - Sign up for an activity
- `DELETE /activities/{name}/unregister?email={email}` - Unregister from an activity

## Database Schema

### Users Table
- `id`: Primary key
- `email`: Unique email address
- `name`: Student name

### Activities Table
- `id`: Primary key
- `name`: Unique activity name
- `description`: Activity description
- `schedule`: Meeting schedule
- `max_participants`: Maximum capacity

### Enrollments Table (Many-to-Many)
- `user_id`: Foreign key to users
- `activity_id`: Foreign key to activities

## Development

### Database Management

**Reset database:**
```bash
sudo -u postgres psql -d school_management -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
cd src
python3 init_db.py
```

**View database contents:**
```bash
# List all users
sudo -u postgres psql -d school_management -c "SELECT * FROM users;"

# List all activities
sudo -u postgres psql -d school_management -c "SELECT * FROM activities;"

# View enrollments
sudo -u postgres psql -d school_management -c "SELECT u.name, a.name as activity FROM users u JOIN enrollments e ON u.id = e.user_id JOIN activities a ON e.activity_id = a.id;"
```

## Troubleshooting

**Database connection errors:**
- Ensure PostgreSQL is running: `sudo systemctl status postgresql`
- Verify credentials in `.env` file match your PostgreSQL setup

**Port already in use:**
- Change the port in the uvicorn command: `--port 8001`

**Import errors:**
- Make sure you're in the `src` directory when running the application
- Verify all dependencies are installed: `pip install -r requirements.txt`
