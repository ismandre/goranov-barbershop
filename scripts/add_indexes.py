"""Add database indexes for improved query performance."""

from sqlalchemy import create_engine, Index, text
from app.database.models import Base, Appointment, AvailableSlot
import os
from dotenv import load_dotenv

load_dotenv()


def add_indexes():
    """Add performance indexes to the database."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./barbershop.db")
    engine = create_engine(database_url)

    print("Adding database indexes...")

    with engine.connect() as conn:
        # Add index on Appointment.status
        # This improves filtering by status (confirmed, cancelled, etc.)
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_appointment_status "
                "ON appointments (status)"
            ))
            print("✓ Created index: idx_appointment_status")
        except Exception as e:
            print(f"⚠ Index idx_appointment_status already exists or error: {e}")

        # Add composite index on AvailableSlot(start_time, is_booked)
        # This improves queries that filter by both time and booking status
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_slot_availability "
                "ON available_slots (start_time, is_booked)"
            ))
            print("✓ Created index: idx_slot_availability")
        except Exception as e:
            print(f"⚠ Index idx_slot_availability already exists or error: {e}")

        # Add index on Appointment.user_id for faster user queries
        try:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_appointment_user "
                "ON appointments (user_id)"
            ))
            print("✓ Created index: idx_appointment_user")
        except Exception as e:
            print(f"⚠ Index idx_appointment_user already exists or error: {e}")

        conn.commit()

    print("\nIndexes added successfully!")
    print("\nTo verify indexes, run:")
    print("  sqlite3 barbershop.db '.schema appointments'")
    print("  sqlite3 barbershop.db '.schema available_slots'")


if __name__ == "__main__":
    add_indexes()
