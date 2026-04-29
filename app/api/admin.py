"""Admin API endpoints for managing appointments and slots."""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.database import get_db_session
from app.database.models import Admin, AvailableSlot, Appointment, User, ConversationHistory
from app.auth import get_current_admin
from app.services.appointment_service import AppointmentService


router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# Pydantic Models
# ============================================================================

class AppointmentResponse(BaseModel):
    """Appointment details for admin view."""
    id: int
    customer_phone: str
    customer_name: Optional[str]
    start_time: str
    end_time: str
    status: str
    booked_at: str
    notes: Optional[str]


class SlotResponse(BaseModel):
    """Available slot details."""
    id: int
    start_time: str
    end_time: str
    is_booked: bool


class CreateSlotRequest(BaseModel):
    """Request to create a new slot."""
    start_time: str  # ISO format: "2024-12-05T10:00:00"
    end_time: str


class UpdateAppointmentRequest(BaseModel):
    """Request to update appointment status."""
    status: str  # pending, confirmed, completed, cancelled, no_show


class StatsResponse(BaseModel):
    """Dashboard statistics."""
    today_appointments: int
    pending_confirmations: int
    available_slots: int
    total_customers: int


class ConversationMessageResponse(BaseModel):
    """Single conversation message."""
    id: int
    message: str
    is_from_user: bool
    timestamp: str


class ConversationHistoryResponse(BaseModel):
    """Paginated conversation history."""
    customer_phone: str
    customer_name: Optional[str]
    messages: List[ConversationMessageResponse]
    total_messages: int
    page: int
    page_size: int
    total_pages: int


# ============================================================================
# Appointments Endpoints
# ============================================================================

@router.get("/appointments", response_model=List[AppointmentResponse])
def get_appointments(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None, description="Filter by status"),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Get all appointments with optional filters.

    **Query Parameters:**
    - `date`: Filter by specific date (YYYY-MM-DD)
    - `status`: Filter by status (pending, confirmed, completed, cancelled, no_show)

    **Example:**
    ```
    GET /admin/appointments?date=2024-12-05&status=pending
    ```
    """
    # Use eager loading to prevent N+1 queries
    # This loads user and slot data in the same query
    query = (
        db.query(Appointment)
        .join(AvailableSlot)
        .join(User)
        .options(
            joinedload(Appointment.user),
            joinedload(Appointment.slot)
        )
    )

    # Filter by date if provided
    if date:
        try:
            filter_date = datetime.fromisoformat(date)
            query = query.filter(
                AvailableSlot.start_time >= filter_date,
                AvailableSlot.start_time < filter_date.replace(hour=23, minute=59, second=59)
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    # Filter by status if provided
    if status:
        query = query.filter(Appointment.status == status)

    appointments = query.order_by(AvailableSlot.start_time).all()

    return [
        AppointmentResponse(
            id=appt.id,
            customer_phone=appt.user.phone_number,
            customer_name=appt.user.name,
            start_time=appt.slot.start_time.isoformat(),
            end_time=appt.slot.end_time.isoformat(),
            status=appt.status,
            booked_at=appt.booked_at.isoformat(),
            notes=appt.notes
        )
        for appt in appointments
    ]


@router.patch("/appointments/{appointment_id}")
def update_appointment_status(
    appointment_id: int,
    update: UpdateAppointmentRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Update appointment status.

    **Valid statuses:** pending, confirmed, completed, cancelled, no_show

    **Example:**
    ```json
    {
        "status": "completed"
    }
    ```
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    # Validate status
    valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled', 'no_show']
    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    appointment.status = update.status
    appointment.updated_at = datetime.utcnow()
    db.commit()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "status": update.status
    }


# ============================================================================
# Slots Endpoints
# ============================================================================

@router.get("/slots", response_model=List[SlotResponse])
def get_slots(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    available_only: bool = Query(False, description="Show only available (unbooked) slots"),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Get all time slots with optional filters.

    **Query Parameters:**
    - `date`: Filter by specific date (YYYY-MM-DD)
    - `available_only`: Show only unbooked slots (true/false)

    **Example:**
    ```
    GET /admin/slots?date=2024-12-05&available_only=true
    ```
    """
    query = db.query(AvailableSlot)

    # Filter by date if provided
    if date:
        try:
            filter_date = datetime.fromisoformat(date)
            query = query.filter(
                AvailableSlot.start_time >= filter_date,
                AvailableSlot.start_time < filter_date.replace(hour=23, minute=59, second=59)
            )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    # Filter by availability if requested
    if available_only:
        query = query.filter(AvailableSlot.is_booked == False)

    slots = query.order_by(AvailableSlot.start_time).all()

    return [
        SlotResponse(
            id=slot.id,
            start_time=slot.start_time.isoformat(),
            end_time=slot.end_time.isoformat(),
            is_booked=slot.is_booked
        )
        for slot in slots
    ]


@router.post("/slots", status_code=status.HTTP_201_CREATED)
def create_slot(
    slot: CreateSlotRequest,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Create a new available time slot.

    **Example:**
    ```json
    {
        "start_time": "2024-12-05T10:00:00",
        "end_time": "2024-12-05T10:30:00"
    }
    ```
    """
    try:
        start = datetime.fromisoformat(slot.start_time)
        end = datetime.fromisoformat(slot.end_time)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS"
        )

    if end <= start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )

    new_slot = AvailableSlot(
        start_time=start,
        end_time=end,
        is_booked=False,
        created_by=admin.id
    )

    db.add(new_slot)
    db.commit()
    db.refresh(new_slot)

    return {
        "success": True,
        "id": new_slot.id,
        "start_time": new_slot.start_time.isoformat(),
        "end_time": new_slot.end_time.isoformat()
    }


@router.delete("/slots/{slot_id}")
def delete_slot(
    slot_id: int,
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Delete a time slot.

    Cannot delete slots that are already booked.
    """
    slot = db.query(AvailableSlot).filter(AvailableSlot.id == slot_id).first()

    if not slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot not found"
        )

    if slot.is_booked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a booked slot"
        )

    db.delete(slot)
    db.commit()

    return {"success": True, "deleted_slot_id": slot_id}


# ============================================================================
# Statistics Endpoint
# ============================================================================

@router.get("/stats", response_model=StatsResponse)
def get_dashboard_stats(
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Get dashboard statistics.

    **Response:**
    ```json
    {
        "today_appointments": 5,
        "pending_confirmations": 2,
        "available_slots": 8,
        "total_customers": 120
    }
    ```
    """
    today = datetime.utcnow().date()
    tomorrow = datetime(today.year, today.month, today.day + 1 if today.day < 28 else 1)

    # Count today's appointments
    today_appointments = db.query(Appointment).join(AvailableSlot).filter(
        AvailableSlot.start_time >= datetime.combine(today, datetime.min.time()),
        AvailableSlot.start_time < tomorrow
    ).count()

    # Count pending confirmations
    pending = db.query(Appointment).filter(Appointment.status == 'pending').count()

    # Count available slots
    available = db.query(AvailableSlot).filter(
        AvailableSlot.is_booked == False,
        AvailableSlot.start_time >= datetime.utcnow()
    ).count()

    # Count total customers
    total_customers = db.query(User).count()

    return StatsResponse(
        today_appointments=today_appointments,
        pending_confirmations=pending,
        available_slots=available,
        total_customers=total_customers
    )


# ============================================================================
# Conversation History Endpoint
# ============================================================================

@router.get("/customers/{phone_number}/conversation", response_model=ConversationHistoryResponse)
def get_customer_conversation(
    phone_number: str,
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    page_size: int = Query(50, ge=1, le=200, description="Messages per page (max 200)"),
    admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db_session)
):
    """
    Get conversation history for a specific customer with pagination.

    **Path Parameters:**
    - `phone_number`: Customer's phone number (e.g., +385991234567)

    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Messages per page, max 200 (default: 50)

    **Response:**
    ```json
    {
        "customer_phone": "+385991234567",
        "customer_name": "Ivan Horvat",
        "messages": [
            {
                "id": 123,
                "message": "Bok, želim zakazati termin",
                "is_from_user": true,
                "timestamp": "2024-12-05T14:30:00Z"
            },
            ...
        ],
        "total_messages": 42,
        "page": 1,
        "page_size": 50,
        "total_pages": 1
    }
    ```
    """
    # Get user by phone number
    user = db.query(User).filter(User.phone_number == phone_number).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with phone {phone_number} not found"
        )

    # Get total message count
    total_messages = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == user.id
    ).count()

    # Calculate pagination
    total_pages = (total_messages + page_size - 1) // page_size  # Ceiling division
    offset = (page - 1) * page_size

    # Get paginated messages (newest first)
    messages = (
        db.query(ConversationHistory)
        .filter(ConversationHistory.user_id == user.id)
        .order_by(ConversationHistory.timestamp.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # Build response
    return ConversationHistoryResponse(
        customer_phone=user.phone_number,
        customer_name=user.name,
        messages=[
            ConversationMessageResponse(
                id=msg.id,
                message=msg.message,
                is_from_user=msg.is_from_user,
                timestamp=msg.timestamp.isoformat()
            )
            for msg in messages
        ],
        total_messages=total_messages,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
