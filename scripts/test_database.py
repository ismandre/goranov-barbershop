#!/usr/bin/env python
"""
Test database operations to verify everything works correctly.

Usage:
    python scripts/test_database.py
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db, User, UserState, AvailableSlot, Appointment


def test_create_user():
    """Test creating a new user."""
    print("Testing user creation...")
    with get_db() as db:
        # Delete existing test user if exists
        existing = db.query(User).filter(User.phone_number == "+385991234567").first()
        if existing:
            # Clean up related data
            db.query(Appointment).filter(Appointment.user_id == existing.id).delete()
            db.query(UserState).filter(UserState.user_id == existing.id).delete()
            db.delete(existing)
            db.commit()

        user = User(
            phone_number="+385991234567",
            name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"  ✅ Created user: {user}")
        return user.id


def test_user_state(user_id):
    """Test creating and updating user state."""
    print("Testing user state...")
    with get_db() as db:
        state = UserState(
            user_id=user_id,
            current_state="StateMainMenu",
            context='{"last_message": "Hello"}'
        )
        db.add(state)
        db.commit()
        print(f"  ✅ Created user state: {state}")


def test_available_slot():
    """Test creating an available slot."""
    print("Testing available slot creation...")
    with get_db() as db:
        start = datetime.now() + timedelta(days=1)
        end = start + timedelta(minutes=30)

        slot = AvailableSlot(
            start_time=start,
            end_time=end,
            is_booked=False
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)
        print(f"  ✅ Created slot: {slot}")
        return slot.id


def test_appointment(user_id, slot_id):
    """Test creating an appointment."""
    print("Testing appointment creation...")
    with get_db() as db:
        appointment = Appointment(
            user_id=user_id,
            slot_id=slot_id,
            status="pending"
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        print(f"  ✅ Created appointment: {appointment}")


def test_queries():
    """Test various queries."""
    print("Testing queries...")
    with get_db() as db:
        # Count users
        user_count = db.query(User).count()
        print(f"  ✅ Total users: {user_count}")

        # Count available slots
        available_count = db.query(AvailableSlot).filter(AvailableSlot.is_booked == False).count()
        print(f"  ✅ Available slots: {available_count}")

        # Count appointments
        appointment_count = db.query(Appointment).count()
        print(f"  ✅ Total appointments: {appointment_count}")


def test_cleanup():
    """Clean up test data."""
    print("Cleaning up test data...")
    with get_db() as db:
        # Delete test user
        test_user = db.query(User).filter(User.phone_number == "+385991234567").first()
        if test_user:
            # Delete appointments first (foreign key constraint)
            db.query(Appointment).filter(Appointment.user_id == test_user.id).delete()
            # Delete user state
            db.query(UserState).filter(UserState.user_id == test_user.id).delete()
            # Delete user
            db.delete(test_user)

        db.commit()
        print("  ✅ Test data cleaned up")


def main():
    print("🧪 Running database tests...")
    print("=" * 50)

    try:
        # Create test data
        user_id = test_create_user()
        test_user_state(user_id)
        slot_id = test_available_slot()
        test_appointment(user_id, slot_id)

        # Run queries
        test_queries()

        # Cleanup
        test_cleanup()

        print("=" * 50)
        print("✅ All tests passed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
