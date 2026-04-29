#!/usr/bin/env python
"""
Create an admin user in the database.

Usage:
    python scripts/create_admin.py

Or with custom credentials:
    python scripts/create_admin.py --username barber --password mypassword
"""

import sys
import argparse
from pathlib import Path
from getpass import getpass

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import get_db
from app.database.models import Admin
from app.auth.password import hash_password


def create_admin(username: str, password: str, phone_number: str = None):
    """Create an admin user with hashed password."""
    # Validate password length (bcrypt has 72 byte limit)
    if len(password.encode('utf-8')) > 72:
        print(f"❌ Password is too long. Please use a password with 72 bytes or less.")
        return False

    with get_db() as db:
        # Check if admin already exists
        existing_admin = db.query(Admin).filter(Admin.username == username).first()
        if existing_admin:
            print(f"❌ Admin user '{username}' already exists!")
            return False

        # Hash password
        password_hash = hash_password(password)

        # Create admin
        admin = Admin(
            username=username,
            password_hash=password_hash,
            phone_number=phone_number
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"✅ Admin user created successfully!")
        print(f"   Username: {username}")
        print(f"   ID: {admin.id}")
        if phone_number:
            print(f"   Phone: {phone_number}")

        return True


def main():
    parser = argparse.ArgumentParser(description="Create an admin user")
    parser.add_argument("--username", type=str, help="Admin username")
    parser.add_argument("--password", type=str, help="Admin password")
    parser.add_argument("--phone", type=str, help="Admin phone number (optional)")

    args = parser.parse_args()

    # Get username
    if args.username:
        username = args.username
    else:
        username = input("Enter username [barber]: ").strip() or "barber"

    # Get password
    if args.password:
        password = args.password
    else:
        password = getpass("Enter password: ")
        password_confirm = getpass("Confirm password: ")

        if password != password_confirm:
            print("❌ Passwords do not match!")
            sys.exit(1)

    # Get phone (optional)
    phone_number = args.phone
    if not phone_number and not args.password:  # Only prompt if in interactive mode
        phone_number = input("Enter phone number (optional, press Enter to skip): ").strip() or None

    # Create admin
    create_admin(username, password, phone_number)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Cancelled by user")
        sys.exit(1)
