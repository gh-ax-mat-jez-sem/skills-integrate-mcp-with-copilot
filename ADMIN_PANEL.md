# Admin Panel

This document explains how to use the admin panel for managing the Mergington High School extracurricular activities system.

## Setup

### Configure Admin Users

Set the `ADMIN_IDS` environment variable with a comma-separated list of admin user IDs:

```bash
export ADMIN_IDS=admin1,admin2,admin3
```

Or create a `.env` file in the `src/` directory (see `.env.example`).

### Start the Application

```bash
cd src
python -m uvicorn app:app --reload
```

## Accessing the Admin Panel

1. Navigate to http://localhost:8000
2. Click on "Admin Panel →" in the header
3. Enter your admin ID (must match one of the IDs in `ADMIN_IDS`)
4. Click "Verify Access"

## Features

### System Statistics Dashboard
- **Total Students**: Number of unique students enrolled in activities
- **Total Activities**: Total number of available activities
- **Total Enrollments**: Sum of all student enrollments across all activities
- **Capacity Utilization**: Percentage of total capacity being used

### Popular Activities
View all activities sorted by enrollment count with:
- Activity name
- Current enrollment numbers
- Maximum capacity
- Utilization percentage (visual bar)
- Schedule

### User Management
- View all registered students
- See which activities each student is enrolled in
- View total activity count per student

### Activity Management
- Create new activities with:
  - Activity name
  - Description
  - Schedule
  - Maximum participants
- Activities are immediately available to students

## API Endpoints

All admin endpoints require the `X-User-ID` header with a valid admin ID.

### GET /admin/stats
Returns system-wide statistics.

### GET /admin/users
Returns list of all students and their enrollments.

### GET /admin/activities/popular
Returns activities sorted by enrollment count.

### POST /admin/activities
Create a new activity.

Request body:
```json
{
  "name": "Activity Name",
  "description": "Activity description",
  "schedule": "Days, Time",
  "max_participants": 20
}
```

### PUT /admin/activities/{activity_name}
Update an existing activity (preserves participants).

### DELETE /admin/activities/{activity_name}
Delete an activity.

## Security

- Admin routes are protected by authentication
- Non-admin users receive 403 Forbidden responses
- Admin IDs should be kept secure and not shared publicly
