"""Test state machine integration with database."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import get_db, User, UserState, AvailableSlot
from app.logic.state_machine import handle_state_transition
from app.services.appointment_service import AppointmentService
from datetime import datetime, timedelta


def cleanup_test_user(phone_number: str):
    """Clean up test user and related data."""
    with get_db() as db:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if user:
            # Clean up related data
            from app.database.models import Appointment, ConversationHistory
            db.query(Appointment).filter(Appointment.user_id == user.id).delete()
            db.query(UserState).filter(UserState.user_id == user.id).delete()
            db.query(ConversationHistory).filter(ConversationHistory.user_id == user.id).delete()
            db.delete(user)
            db.commit()


def create_test_slots():
    """Create test slots for booking."""
    with get_db() as db:
        # Create 3 test slots
        slots = []
        base_time = datetime.now() + timedelta(days=1)

        for i in range(3):
            start = base_time.replace(hour=10+i, minute=0, second=0, microsecond=0)
            end = start + timedelta(minutes=30)

            slot = AvailableSlot(
                start_time=start,
                end_time=end,
                is_booked=False
            )
            db.add(slot)
            slots.append(slot)

        db.commit()
        print(f"✅ Created {len(slots)} test slots")


def test_conversation_flow():
    """Test a complete conversation flow."""
    test_phone = "+385991234567"

    print("🧪 Testing State Machine Integration")
    print("=" * 60)

    # Clean up any existing test data
    cleanup_test_user(test_phone)

    # Create test slots
    create_test_slots()

    print("\n1️⃣ New user sends first message")
    response = handle_state_transition(test_phone, "Bok!")
    print(f"Bot: {response}\n")
    assert "Dobrodošli" in response or "Bok" in response

    print("2️⃣ User wants to see available slots")
    response = handle_state_transition(test_phone, "1")
    print(f"Bot: {response}\n")
    assert "slobodnih termina" in response or "termina" in response

    print("3️⃣ User selects slot #1")
    response = handle_state_transition(test_phone, "1")
    print(f"Bot: {response}\n")
    assert "Želite li potvrditi" in response or "potvrdi" in response.lower()

    print("4️⃣ User confirms booking")
    response = handle_state_transition(test_phone, "da")
    print(f"Bot: {response}\n")
    assert "potvrđen" in response or "Vidimo se" in response

    print("5️⃣ Check that appointment was created")
    with get_db() as db:
        user = db.query(User).filter(User.phone_number == test_phone).first()
        appointments = AppointmentService.get_active_appointments(db, user.id)
        print(f"✅ User has {len(appointments)} active appointment(s)")
        assert len(appointments) == 1

    print("6️⃣ User checks their reservations")
    response = handle_state_transition(test_phone, "2")
    print(f"Bot: {response}\n")
    assert "rezervacije" in response.lower()

    # Cleanup
    cleanup_test_user(test_phone)
    print("\n" + "=" * 60)
    print("✅ All conversation flow tests passed!")


def test_edge_cases():
    """Test edge cases and error handling."""
    test_phone = "+385997654321"

    print("\n🧪 Testing Edge Cases")
    print("=" * 60)

    cleanup_test_user(test_phone)

    print("\n1️⃣ Invalid slot selection")
    response = handle_state_transition(test_phone, "Bok")
    response = handle_state_transition(test_phone, "1")  # Show slots
    response = handle_state_transition(test_phone, "999")  # Invalid number
    print(f"Bot: {response}")
    assert "nevažeći" in response.lower() or "invalid" in response.lower()

    print("\n2️⃣ No reservations check")
    cleanup_test_user(test_phone)
    response = handle_state_transition(test_phone, "Bok")
    response = handle_state_transition(test_phone, "2")  # My reservations
    print(f"Bot: {response}")
    assert "nemate" in response.lower() or "no" in response.lower()

    cleanup_test_user(test_phone)
    print("\n" + "=" * 60)
    print("✅ All edge case tests passed!")


if __name__ == "__main__":
    try:
        test_conversation_flow()
        test_edge_cases()
        print("\n🎉 All tests passed successfully!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
