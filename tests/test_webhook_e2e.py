"""End-to-end tests for WhatsApp webhook."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.database.models import User, AvailableSlot, UserState, ConversationHistory


@pytest.mark.e2e
def test_complete_booking_flow(client: TestClient, test_db_session):
    """Test complete booking flow from greeting to confirmed appointment."""
    phone = "+385991234567"

    # Create available slots
    base_time = datetime.utcnow() + timedelta(days=1)
    for i in range(3):
        slot = AvailableSlot(
            start_time=base_time + timedelta(hours=i),
            end_time=base_time + timedelta(hours=i, minutes=30),
            is_booked=False
        )
        test_db_session.add(slot)
    test_db_session.commit()

    # Step 1: Initial greeting (user unknown)
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "Bok"}
    )
    assert response.status_code == 200
    assert "text/xml" in response.headers["content-type"] or "application/xml" in response.headers["content-type"]

    # Verify user was created
    user = test_db_session.query(User).filter(User.phone_number == phone).first()
    assert user is not None

    # Step 2: Provide name
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "Ivan"}
    )
    assert response.status_code == 200

    # Verify user name was saved
    test_db_session.refresh(user)
    assert user.name == "Ivan"

    # Step 3: Request available appointments
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "1"}
    )
    assert response.status_code == 200

    # Step 4: Select appointment (choose slot 1)
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "1"}
    )
    assert response.status_code == 200

    # Step 5: Confirm booking
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "da"}
    )
    assert response.status_code == 200

    # Verify appointment was created
    from app.database.models import Appointment
    appointment = test_db_session.query(Appointment).filter(
        Appointment.user_id == user.id
    ).first()
    assert appointment is not None
    assert appointment.status == 'confirmed'


@pytest.mark.e2e
def test_webhook_error_handling_missing_params(client: TestClient):
    """Test webhook handles missing parameters gracefully."""
    # Missing Body parameter
    response = client.post(
        "/whatsapp/webhook",
        data={"From": "+385991234567"}
    )
    # Should return 422 for validation error
    assert response.status_code == 422

    # Missing From parameter
    response = client.post(
        "/whatsapp/webhook",
        data={"Body": "Hello"}
    )
    assert response.status_code == 422


@pytest.mark.e2e
def test_webhook_very_long_message(client: TestClient, test_db_session):
    """Test webhook handles very long messages."""
    phone = "+385991111111"

    # Create user first
    user = User(phone_number=phone, name="Test User")
    test_db_session.add(user)
    user_state = UserState(
        user_id=1,
        current_state='StateMainMenu',
        context='{}'
    )
    test_db_session.add(user_state)
    test_db_session.commit()

    # Send very long message (1000 characters)
    long_message = "A" * 1000

    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": long_message}
    )

    # Should still process (though may not understand)
    assert response.status_code == 200


@pytest.mark.e2e
def test_invalid_slot_selection(client: TestClient, test_db_session):
    """Test selecting invalid slot number."""
    phone = "+385992222222"

    # Create user in state waiting for slot selection
    user = User(phone_number=phone, name="Test User")
    test_db_session.add(user)
    test_db_session.commit()

    # Create just 2 slots
    base_time = datetime.utcnow() + timedelta(days=1)
    for i in range(2):
        slot = AvailableSlot(
            start_time=base_time + timedelta(hours=i),
            end_time=base_time + timedelta(hours=i, minutes=30),
            is_booked=False
        )
        test_db_session.add(slot)
    test_db_session.commit()

    # Navigate to slot selection
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "1"}  # Show available
    )
    assert response.status_code == 200

    # Try to select slot 5 (doesn't exist)
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "5"}
    )
    assert response.status_code == 200
    # Should get some response (error or reprompt)


@pytest.mark.e2e
def test_cancel_reservation_flow(client: TestClient, test_db_session):
    """Test cancelling an existing reservation."""
    phone = "+385993333333"

    # Create user with an existing appointment
    user = User(phone_number=phone, name="Test User")
    test_db_session.add(user)
    test_db_session.commit()

    slot = AvailableSlot(
        start_time=datetime.utcnow() + timedelta(days=1),
        end_time=datetime.utcnow() + timedelta(days=1, minutes=30),
        is_booked=True
    )
    test_db_session.add(slot)
    test_db_session.commit()

    from app.database.models import Appointment
    appointment = Appointment(
        user_id=user.id,
        slot_id=slot.id,
        status='confirmed'
    )
    test_db_session.add(appointment)
    test_db_session.commit()

    # Navigate to main menu and select "show my reservations"
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "2"}
    )
    assert response.status_code == 200

    # Select the reservation to cancel (option 1)
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "1"}
    )
    assert response.status_code == 200

    # Confirm cancellation
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "da"}
    )
    assert response.status_code == 200

    # Verify appointment was cancelled
    test_db_session.refresh(appointment)
    assert appointment.status == 'cancelled'

    # Verify slot was freed
    test_db_session.refresh(slot)
    assert slot.is_booked is False


@pytest.mark.e2e
def test_conversation_history_tracking(client: TestClient, test_db_session):
    """Test that conversation history is properly tracked."""
    phone = "+385994444444"

    # Send a message
    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "Hello"}
    )
    assert response.status_code == 200

    # Check conversation history was created
    user = test_db_session.query(User).filter(User.phone_number == phone).first()
    assert user is not None

    history = test_db_session.query(ConversationHistory).filter(
        ConversationHistory.user_id == user.id
    ).all()

    # Should have at least the incoming message
    assert len(history) >= 1
    incoming_msg = next((h for h in history if h.direction == 'incoming'), None)
    assert incoming_msg is not None
    assert incoming_msg.message == "Hello"


@pytest.mark.e2e
def test_multiple_users_concurrent_sessions(client: TestClient, test_db_session):
    """Test that multiple users can have independent sessions."""
    user1_phone = "+385995555555"
    user2_phone = "+385996666666"

    # User 1 starts conversation
    response1 = client.post(
        "/whatsapp/webhook",
        data={"From": user1_phone, "Body": "Bok"}
    )
    assert response1.status_code == 200

    # User 2 starts conversation
    response2 = client.post(
        "/whatsapp/webhook",
        data={"From": user2_phone, "Body": "Bok"}
    )
    assert response2.status_code == 200

    # Verify both users exist and have separate states
    user1 = test_db_session.query(User).filter(User.phone_number == user1_phone).first()
    user2 = test_db_session.query(User).filter(User.phone_number == user2_phone).first()

    assert user1 is not None
    assert user2 is not None
    assert user1.id != user2.id

    state1 = test_db_session.query(UserState).filter(UserState.user_id == user1.id).first()
    state2 = test_db_session.query(UserState).filter(UserState.user_id == user2.id).first()

    assert state1 is not None
    assert state2 is not None


@pytest.mark.e2e
def test_webhook_returns_valid_twiml(client: TestClient):
    """Test that webhook returns valid TwiML XML response."""
    phone = "+385997777777"

    response = client.post(
        "/whatsapp/webhook",
        data={"From": phone, "Body": "Test"}
    )

    assert response.status_code == 200
    content_type = response.headers.get("content-type", "")
    assert "xml" in content_type.lower()

    # Check response contains TwiML tags
    content = response.text
    assert "<Response>" in content or "<Message>" in content
