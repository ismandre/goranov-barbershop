"""Service layer for appointment-related operations."""

from datetime import datetime
from typing import List, Optional, Any

from sqlalchemy.orm import Session

from app.database.models import AvailableSlot, Appointment
from app.logging_config import get_logger

logger = get_logger(__name__)


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
        """Book an appointment if slot is available.

        Uses pessimistic locking (SELECT FOR UPDATE) to prevent race conditions
        where multiple concurrent requests try to book the same slot.
        """
        # Check if slot exists and is available with row-level lock
        # This prevents other transactions from reading/modifying this row
        # until our transaction completes (commit or rollback)
        slot = db.query(AvailableSlot).filter(
            AvailableSlot.id == slot_id
        ).with_for_update().first()

        # Verify slot exists and is not already booked
        if not slot or slot.is_booked:
            if slot and slot.is_booked:
                logger.warning(
                    f"Attempted to book already booked slot",
                    extra={"user_id": user_id, "slot_id": slot_id}
                )
            else:
                logger.warning(
                    f"Attempted to book non-existent slot",
                    extra={"user_id": user_id, "slot_id": slot_id}
                )
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

        logger.info(
            f"Appointment booked successfully",
            extra={
                "user_id": user_id,
                "slot_id": slot_id,
                "appointment_id": appointment.id,
                "start_time": slot.start_time.isoformat()
            }
        )

        return appointment

    @staticmethod
    def cancel_appointment(db: Session, appointment_id: int, user_id: int) -> bool:
        """Cancel an appointment and free up the slot."""
        appointment = db.query(Appointment).filter(
            Appointment.id == appointment_id,
            Appointment.user_id == user_id
        ).first()

        if not appointment:
            logger.warning(
                f"Attempted to cancel non-existent or unauthorized appointment",
                extra={"appointment_id": appointment_id, "user_id": user_id}
            )
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

        logger.info(
            f"Appointment cancelled successfully",
            extra={
                "appointment_id": appointment_id,
                "user_id": user_id,
                "slot_id": appointment.slot_id
            }
        )

        return True

    @staticmethod
    def get_slot_by_id(db: Session, slot_id: int) -> Optional[AvailableSlot]:
        """Get a specific slot by ID."""
        return db.query(AvailableSlot).filter(AvailableSlot.id == slot_id).first()
