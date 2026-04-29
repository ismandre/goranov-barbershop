#!/usr/bin/env python
"""
Manual testing script for Goranov Barbershop conversation flow.

Usage:
    python manual_test.py [phone_number]

Example:
    python manual_test.py +385991234567
"""

import sys
from app.logic.state_machine import handle_state_transition
from app.database import get_db
from app.database.models import User, Appointment, UserState, ConversationHistory


def cleanup_user(phone_number: str):
    """Clean up existing test user data."""
    with get_db() as db:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if user:
            db.query(ConversationHistory).filter(ConversationHistory.user_id == user.id).delete()
            db.query(Appointment).filter(Appointment.user_id == user.id).delete()
            db.query(UserState).filter(UserState.user_id == user.id).delete()
            db.delete(user)
            db.commit()
            print(f"🧹 Cleaned up existing data for {phone_number}\n")


def verify_booking(phone_number: str):
    """Verify appointment was created."""
    with get_db() as db:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if user:
            appointments = db.query(Appointment).filter(Appointment.user_id == user.id).all()
            print(f"\n📊 Verification:")
            print(f"   User ID: {user.id}")
            print(f"   Appointments: {len(appointments)}")
            for appt in appointments:
                print(f"   - Status: {appt.status}")
                print(f"     Time: {appt.slot.start_time}")
                print(f"     Slot ID: {appt.slot_id}")


def test_booking_flow(phone_number: str, cleanup: bool = True):
    """Test complete booking flow."""

    if cleanup:
        cleanup_user(phone_number)

    print("=" * 60)
    print("GORANOV BARBERSHOP - BOOKING FLOW TEST")
    print("=" * 60)

    # Step 1: Welcome
    print("\n📱 Step 1: Initial Contact")
    print("👤 User: Bok!")
    response = handle_state_transition(phone_number, "Bok")
    print(f"🤖 Bot:\n{response}\n")
    input("Press Enter to continue...")

    # Step 2: Show available slots
    print("\n📱 Step 2: Request Available Slots")
    print("👤 User: 1")
    response = handle_state_transition(phone_number, "1")
    print(f"🤖 Bot:\n{response}\n")
    input("Press Enter to continue...")

    # Step 3: Select slot
    print("\n📱 Step 3: Select First Slot")
    print("👤 User: 1")
    response = handle_state_transition(phone_number, "1")
    print(f"🤖 Bot:\n{response}\n")
    input("Press Enter to continue...")

    # Step 4: Confirm booking
    print("\n📱 Step 4: Confirm Booking")
    print("👤 User: da")
    response = handle_state_transition(phone_number, "da")
    print(f"🤖 Bot:\n{response}\n")

    print("=" * 60)
    print("✅ Booking flow complete!")
    print("=" * 60)

    verify_booking(phone_number)


def test_edge_cases(phone_number: str):
    """Test error handling and edge cases."""

    cleanup_user(phone_number)

    print("\n" + "=" * 60)
    print("EDGE CASE TESTING")
    print("=" * 60)

    # Test invalid slot selection
    print("\n🔍 Test: Invalid slot number")
    handle_state_transition(phone_number, "Bok")
    handle_state_transition(phone_number, "1")  # Show slots
    response = handle_state_transition(phone_number, "999")
    print(f"🤖 Bot: {response}\n")

    # Test no reservations
    cleanup_user(phone_number)
    print("\n🔍 Test: No reservations")
    handle_state_transition(phone_number, "Bok")
    response = handle_state_transition(phone_number, "2")  # My reservations
    print(f"🤖 Bot: {response}\n")

    print("=" * 60)
    print("✅ Edge case testing complete!")
    print("=" * 60)


def interactive_mode(phone_number: str):
    """Interactive testing mode."""

    print("\n" + "=" * 60)
    print("INTERACTIVE MODE")
    print("=" * 60)
    print(f"Testing as: {phone_number}")
    print("Type messages as if you're the user.")
    print("Type 'quit' to exit, 'reset' to clean up user data.\n")

    while True:
        try:
            user_message = input("👤 User: ").strip()

            if user_message.lower() == 'quit':
                print("Goodbye! 👋")
                break

            if user_message.lower() == 'reset':
                cleanup_user(phone_number)
                continue

            if not user_message:
                continue

            response = handle_state_transition(phone_number, user_message)
            print(f"🤖 Bot:\n{response}\n")

        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Manual testing for Goranov Barbershop bot")
    parser.add_argument(
        "phone",
        nargs="?",
        default="+385991234567",
        help="Phone number to test with (default: +385991234567)"
    )
    parser.add_argument(
        "--mode",
        choices=["flow", "edge", "interactive"],
        default="flow",
        help="Test mode (default: flow)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't clean up existing user data before test"
    )

    args = parser.parse_args()

    try:
        if args.mode == "flow":
            test_booking_flow(args.phone, cleanup=not args.no_cleanup)
        elif args.mode == "edge":
            test_edge_cases(args.phone)
        elif args.mode == "interactive":
            interactive_mode(args.phone)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
