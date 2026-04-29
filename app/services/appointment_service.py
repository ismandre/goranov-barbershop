"""Service layer for appointment-related operations."""

from datetime import datetime
from typing import List, Optional, Any

from sqlalchemy.orm import Session

from app.database.models import AvailableSlot, Appointment


class AppointmentService:
    """Handle appointment and slot operations."""

    @staticmethod
    def get_available_slots(db: Session, limit: int = 10) -> list[type[AvailableSlot]]:
        """Get available (unbooked) slots, sorted by start time."""
        return (
            db.query(AvailableSlot)
            .filter(
                AvailableSlot.is_booked == False,
                AvailableSlot.start_time >= datetime.utcnow()
            )
            .order_by(AvailableSlot.start_time)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_appointments(
        db: Session,
        user_id: int,
        status: Optional[str] = None
    ) -> list[type[Appointment]]:
        """Get user's appointments, optionally filtered by status."""
        query = (
            db.query(Appointment)
            .filter(Appointment.user_id == user_id)
        )

        if status:
            query = query.filter(Appointment.status == status)

        return query.order_by(Appointment.booked_at.desc()).all()

    @staticmethod
    def get_active_appointments(db: Session, user_id: int) -> list[type[Appointment]]:
        """Get user's active (pending/confirmed) appointments."""
        return (
            db.query(Appointment)
            .join(AvailableSlot)
            .filter(
                Appointment.user_id == user_id,
                Appointment.status.in_(['pending', 'confirmed']),
                AvailableSlot.start_time >= datetime.utcnow()
            )
            .order_by(AvailableSlot.start_time)
            .all()
        )

    @staticmethod
    def book_appointment(
        db: Session,
        user_id: int,
        slot_id: int,
        notes: Optional[str] = None
    ) -> Optional[Appointment]:
        """Book an appointment if slot is available."""
        # Check if slot exists and is available
        slot = db.query(AvailableSlot).filter(
            AvailableSlot.id == slot_id,
            AvailableSlot.is_booked == False
        ).first()

        if not slot:
            return None

        # Create appointment
        appointment = Appointment(
            user_id=user_id,
            slot_id=slot_id,
            status='confirmed',
            notes=notes
        )

        # Mark slot as booked
        slot.is_booked = True

        db.add(appointment)
        db.commit()
        db.refresh(appointment)

        return appointment

    @staticmethod
    def cancel_appointment(db: Session, appointment_id: int, user_id: int) -> bool:
        """Cancel an appointment and free up the slot."""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id
        ).first()

        if not appointment:
            return False

        # Update appointment status
        appointment.status = 'cancelled'
        appointment.updated_at = datetime.utcnow()

        # Free up the slot
        slot = db.query(AvailableSlot).filter(
            AvailableSlot.id == appointment.slot_id
        ).first()

        if slot:
            slot.is_booked = False

        db.commit()
        return True

    @staticmethod
    def get_slot_by_id(db: Session, slot_id: int) -> Optional[AvailableSlot]:
        """Get a specific slot by ID."""
        return db.query(AvailableSlot).filter(AvailableSlot.id == slot_id).first()
