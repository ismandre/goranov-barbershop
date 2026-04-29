#!/usr/bin/env python
"""
Seed the database with initial available time slots.

Usage:
    python scripts/seed_slots.py

This will create slots for the next 7 days, Monday-Friday, 9AM-5PM, 30-minute intervals.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import get_db
from app.database.models import AvailableSlot


def create_slot(db, start_time: datetime, end_time: datetime):
    """Create a single time slot."""
    slot = AvailableSlot(
        start_time=start_time,
        end_time=end_time,
        is_booked=False
    )
    db.add(slot)
    return slot


def seed_slots_for_week():
    """Create slots for the next 7 days, Monday-Friday, 9AM-5PM."""
    with get_db() as db:
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        slots_created = 0

        # Generate slots for next 7 days
        for day_offset in range(7):
            current_day = today + timedelta(days=day_offset)

            # Skip weekends (Saturday=5, Sunday=6)
            if current_day.weekday() >= 5:
                continue

            # Create slots from 9AM to 5PM (last slot starts at 4:30PM)
            start_hour = 9
            end_hour = 17
            slot_duration_minutes = 30

            current_time = current_day.replace(hour=start_hour, minute=0)
            end_of_day = current_day.replace(hour=end_hour, minute=0)

            while current_time < end_of_day:
                slot_end = current_time + timedelta(minutes=slot_duration_minutes)
                create_slot(db, current_time, slot_end)
                current_time = slot_end
                slots_created += 1

        db.commit()
        print(f"✅ Created {slots_created} available time slots!")
        print(f"   Date range: {today.date()} to {(today + timedelta(days=6)).date()}")
        print(f"   Working hours: 9:00 AM - 5:00 PM")
        print(f"   Slot duration: 30 minutes")
        print(f"   Days: Monday-Friday only")


def seed_custom_slots(date_str: str, start_hour: int, end_hour: int, duration_minutes: int = 30):
    """
    Create custom slots for a specific date.

    Args:
        date_str: Date in format 'YYYY-MM-DD'
        start_hour: Starting hour (24-hour format)
        end_hour: Ending hour (24-hour format)
        duration_minutes: Duration of each slot in minutes
    """
    with get_db() as db:
        target_date = datetime.strptime(date_str, '%Y-%m-%d')
        current_time = target_date.replace(hour=start_hour, minute=0)
        end_time = target_date.replace(hour=end_hour, minute=0)

        slots_created = 0
        while current_time < end_time:
            slot_end = current_time + timedelta(minutes=duration_minutes)
            create_slot(db, current_time, slot_end)
            current_time = slot_end
            slots_created += 1

        db.commit()
        print(f"✅ Created {slots_created} slots for {date_str}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Seed available time slots")
    parser.add_argument("--date", type=str, help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--start-hour", type=int, default=9, help="Start hour (default: 9)")
    parser.add_argument("--end-hour", type=int, default=17, help="End hour (default: 17)")
    parser.add_argument("--duration", type=int, default=30, help="Slot duration in minutes (default: 30)")

    args = parser.parse_args()

    print("🚀 Seeding time slots...")
    print("=" * 50)

    if args.date:
        seed_custom_slots(args.date, args.start_hour, args.end_hour, args.duration)
    else:
        seed_slots_for_week()

    print("=" * 50)
    print("✅ Seeding complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
