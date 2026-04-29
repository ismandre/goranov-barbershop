# Database Setup Guide

## Overview

This project uses SQLite as the database, managed through SQLAlchemy ORM.

## Database Schema

The database consists of 6 main tables:

1. **users** - Customer information (phone number, name, timestamps)
2. **user_states** - Current state in conversation flow for each user
3. **available_slots** - Time slots available for booking
4. **appointments** - Booked appointments linking users to slots
5. **admins** - Admin users who manage the system
6. **conversation_history** - Log of all messages exchanged

For detailed schema, see [DESIGN.md](DESIGN.md#41-tables).

## Setup Instructions

### 1. Initialize the Database

Run the initialization script to create all tables:

```bash
python scripts/init_database.py
```

This will create a `barbershop.db` file in the project root.

### 2. Create an Admin User

Create an admin user to access the dashboard:

```bash
python scripts/create_admin.py
```

You will be prompted for:
- Username (default: `barber`)
- Password
- Phone number (optional)

Or use command-line arguments:

```bash
python scripts/create_admin.py --username admin --password mypassword --phone +385123456789
```

### 3. Seed Initial Slots (Optional)

Populate the database with available time slots:

```bash
# Create slots for the next 7 days (Mon-Fri, 9AM-5PM, 30min intervals)
python scripts/seed_slots.py

# Or create slots for a specific date
python scripts/seed_slots.py --date 2024-12-10 --start-hour 9 --end-hour 17 --duration 30
```

## Database Operations

### Using the Database in Code

```python
from app.database import get_db, User, Appointment

# Query users
with get_db() as db:
    user = db.query(User).filter(User.phone_number == "+385123456789").first()

    if user:
        # Get user's appointments
        appointments = db.query(Appointment).filter(Appointment.user_id == user.id).all()
```

### Direct SQL Access

You can access the database directly using SQLite CLI:

```bash
sqlite3 barbershop.db
```

Useful queries:

```sql
-- List all tables
.tables

-- Show table schema
.schema users

-- Query users
SELECT * FROM users;

-- Query available slots
SELECT * FROM available_slots WHERE is_booked = 0;

-- Query appointments with user info
SELECT
    a.id,
    u.phone_number,
    u.name,
    s.start_time,
    s.end_time,
    a.status
FROM appointments a
JOIN users u ON a.user_id = u.id
JOIN available_slots s ON a.slot_id = s.id
ORDER BY s.start_time;
```

## Resetting the Database

**⚠️ WARNING: This will delete all data!**

To reset the database, simply delete the database file and reinitialize:

```bash
rm barbershop.db
python scripts/init_database.py
python scripts/create_admin.py
python scripts/seed_slots.py
```

## Database Migrations

Currently, the project uses a simple table creation approach. For production, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
```

## Backup & Restore

### Backup

```bash
# Copy database file
cp barbershop.db barbershop_backup_$(date +%Y%m%d_%H%M%S).db

# Or export to SQL
sqlite3 barbershop.db .dump > barbershop_backup.sql
```

### Restore

```bash
# Restore from backup file
cp barbershop_backup_20241205_120000.db barbershop.db

# Or restore from SQL dump
sqlite3 barbershop.db < barbershop_backup.sql
```

## Troubleshooting

### Database Locked Error

If you get a "database is locked" error:

1. Check if any other process is accessing the database
2. Close any open SQLite connections
3. Restart the application

### Table Already Exists

If you get "table already exists" error:

1. The database is already initialized
2. Drop and recreate: `rm barbershop.db && python scripts/init_database.py`

### Schema Changes

After modifying models in `app/database/models.py`:

1. Drop the database: `rm barbershop.db`
2. Reinitialize: `python scripts/init_database.py`
3. Recreate admin and seed data

**Note**: In production, use Alembic migrations instead of dropping tables.
