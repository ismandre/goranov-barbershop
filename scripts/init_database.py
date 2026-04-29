#!/usr/bin/env python
"""
Initialize the database by creating all tables.
Run this script once to set up the database schema.

Usage:
    python scripts/init_database.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import init_db, drop_all_tables


def main():
    print("🚀 Initializing database...")
    print("=" * 50)

    # Uncomment the following line if you want to drop all tables first (CAUTION!)
    # drop_all_tables()

    # Create all tables
    init_db()

    print("=" * 50)
    print("✅ Database initialization complete!")
    print("\nTables created:")
    print("  - users")
    print("  - user_states")
    print("  - available_slots")
    print("  - appointments")
    print("  - admins")
    print("  - conversation_history")
    print("\nNext steps:")
    print("  1. Create an admin user: python scripts/create_admin.py")
    print("  2. Seed initial slots: python scripts/seed_slots.py")


if __name__ == "__main__":
    main()
