"""Unit tests for AppointmentService."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.database.models import User, AvailableSlot, Appointment
from app.services.appointment_service import AppointmentService


@pytest.mark.unit
def test_get_available_slots(test_db_session: Session, test_slots: list):
    """Test retrieving available slots."""
    available = AppointmentService.get_available_slots(test_db_session, limit=10)

    assert len(available) == 5
    assert all(not slot.is_booked for slot in available)
    assert all(slot.start_time >= datetime.utcnow() for slot in available)


@pytest.mark.unit
def test_get_available_slots_excludes_booked(test_db_session: Session, test_slots: list):
    """Test that booked slots are excluded from available slots."""
    # Book the first slot
    test_slots[0].is_booked = True
    test_db_session.commit()

    available = AppointmentService.get_available_slots(test_db_session, limit=10)

    assert len(available) == 4
    assert test_slots[0] not in available


@pytest.mark.unit
def test_get_available_slots_excludes_past(test_db_session: Session):
    """Test that past slots are not returned."""
    # Create a past slot
    past_slot = AvailableSlot(
        start_time=datetime.utcnow() - timedelta(hours=2),
        end_time=datetime.utcnow() - timedelta(hours=1, minutes=30),
        is_booked=False
    )
    test_db_session.add(past_slot)

    # Create a future slot
    future_slot = AvailableSlot(
        start_time=datetime.utcnow() + timedelta(hours=2),
        end_time=datetime.utcnow() + timedelta(hours=2, minutes=30),
        is_booked=False
    )
    test_db_session.add(future_slot)
    test_db_session.commit()

    available = AppointmentService.get_available_slots(test_db_session, limit=10)

    assert past_slot not in available
    assert future_slot in available


@pytest.mark.unit
def test_get_available_slots_limit(test_db_session: Session, test_slots: list):
    """Test that limit parameter works correctly."""
    available = AppointmentService.get_available_slots(test_db_session, limit=3)

    assert len(available) == 3


@pytest.mark.unit
def test_book_appointment_success(test_db_session: Session, test_user: User, test_slots: list):
    """Test successful appointment booking."""
    slot = test_slots[0]
    initial_is_booked = slot.is_booked

    appointment = AppointmentService.book_appointment(
        db=test_db_session,
        user_id=test_user.id,
        slot_id=slot.id,
        notes="Test booking"
    )

    assert appointment is not None
    assert appointment.user_id == test_user.id
    assert appointment.slot_id == slot.id
    assert appointment.status == 'confirmed'
    assert appointment.notes == "Test booking"
    assert initial_is_booked is False

    # Verify slot is marked as booked
    test_db_session.refresh(slot)
    assert slot.is_booked is True


@pytest.mark.unit
def test_book_appointment_already_booked(test_db_session: Session, test_user: User, test_slots: list):
    """Test that booking an already booked slot returns None."""
    slot = test_slots[0]
    slot.is_booked = True
    test_db_session.commit()

    appointment = AppointmentService.book_appointment(
        db=test_db_session,
        user_id=test_user.id,
        slot_id=slot.id
    )

    assert appointment is None


@pytest.mark.unit
def test_book_appointment_nonexistent_slot(test_db_session: Session, test_user: User):
    """Test booking with non-existent slot ID returns None."""
    appointment = AppointmentService.book_appointment(
        db=test_db_session,
        user_id=test_user.id,
        slot_id=99999
    )

    assert appointment is None


@pytest.mark.unit
def test_get_user_appointments(test_db_session: Session, test_user: User, test_appointment: Appointment):
    """Test retrieving user's appointments."""
    appointments = AppointmentService.get_user_appointments(
        db=test_db_session,
        user_id=test_user.id
    )

    assert len(appointments) == 1
    assert appointments[0].id == test_appointment.id


@pytest.mark.unit
def test_get_user_appointments_filter_by_status(test_db_session: Session, test_user: User, test_slots: list):
    """Test filtering appointments by status."""
    # Create appointments with different statuses
    confirmed_appt = Appointment(
        user_id=test_user.id,
        slot_id=test_slots[0].id,
        status='confirmed'
    )
    cancelled_appt = Appointment(
        user_id=test_user.id,
        slot_id=test_slots[1].id,
        status='cancelled'
    )
    test_db_session.add(confirmed_appt)
    test_db_session.add(cancelled_appt)
    test_slots[0].is_booked = True
    test_slots[1].is_booked = True
    test_db_session.commit()

    confirmed_only = AppointmentService.get_user_appointments(
        db=test_db_session,
        user_id=test_user.id,
        status='confirmed'
    )

    assert len(confirmed_only) == 1
    assert confirmed_only[0].status == 'confirmed'


@pytest.mark.unit
def test_get_active_appointments(test_db_session: Session, test_user: User, test_slots: list):
    """Test retrieving only active (pending/confirmed) future appointments."""
    # Create future confirmed appointment
    future_confirmed = Appointment(
        user_id=test_user.id,
        slot_id=test_slots[0].id,
        status='confirmed'
    )
    test_slots[0].is_booked = True

    # Create cancelled appointment (should not appear)
    cancelled = Appointment(
        user_id=test_user.id,
        slot_id=test_slots[1].id,
        status='cancelled'
    )

    test_db_session.add(future_confirmed)
    test_db_session.add(cancelled)
    test_db_session.commit()

    active = AppointmentService.get_active_appointments(
        db=test_db_session,
        user_id=test_user.id
    )

    assert len(active) == 1
    assert active[0].status == 'confirmed'


@pytest.mark.unit
def test_cancel_appointment(test_db_session: Session, test_user: User, test_appointment: Appointment):
    """Test cancelling an appointment."""
    slot_id = test_appointment.slot_id

    result = AppointmentService.cancel_appointment(
        db=test_db_session,
        appointment_id=test_appointment.id,
        user_id=test_user.id
    )

    assert result is True

    # Verify appointment is cancelled
    test_db_session.refresh(test_appointment)
    assert test_appointment.status == 'cancelled'

    # Verify slot is freed
    slot = AppointmentService.get_slot_by_id(test_db_session, slot_id)
    assert slot.is_booked is False


@pytest.mark.unit
def test_cancel_appointment_wrong_user(test_db_session: Session, test_appointment: Appointment):
    """Test that users cannot cancel other users' appointments."""
    # Create another user
    other_user = User(phone_number="+385999999999", name="Other User")
    test_db_session.add(other_user)
    test_db_session.commit()

    result = AppointmentService.cancel_appointment(
        db=test_db_session,
        appointment_id=test_appointment.id,
        user_id=other_user.id
    )

    assert result is False


@pytest.mark.unit
def test_cancel_nonexistent_appointment(test_db_session: Session, test_user: User):
    """Test cancelling non-existent appointment returns False."""
    result = AppointmentService.cancel_appointment(
        db=test_db_session,
        appointment_id=99999,
        user_id=test_user.id
    )

    assert result is False


@pytest.mark.unit
def test_get_slot_by_id(test_db_session: Session, test_slots: list):
    """Test retrieving a specific slot by ID."""
    slot = AppointmentService.get_slot_by_id(test_db_session, test_slots[0].id)

    assert slot is not None
    assert slot.id == test_slots[0].id


@pytest.mark.unit
def test_get_slot_by_id_nonexistent(test_db_session: Session):
    """Test getting non-existent slot returns None."""
    slot = AppointmentService.get_slot_by_id(test_db_session, 99999)

    assert slot is None
