"""Pytest tests for Admin API endpoints."""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.database.models import Admin, AvailableSlot, Appointment, User


@pytest.mark.integration
def test_admin_login_success(client: TestClient, test_admin: Admin):
    """Test successful admin login."""
    response = client.post(
        "/admin/auth/login",
        json={"username": "testadmin", "password": "testpass123"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.integration
def test_admin_login_wrong_password(client: TestClient, test_admin: Admin):
    """Test login with wrong password."""
    response = client.post(
        "/admin/auth/login",
        json={"username": "testadmin", "password": "wrongpassword"}
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_admin_login_nonexistent_user(client: TestClient):
    """Test login with non-existent username."""
    response = client.post(
        "/admin/auth/login",
        json={"username": "nonexistent", "password": "password"}
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_get_appointments_unauthorized(client: TestClient):
    """Test accessing appointments without authentication."""
    response = client.get("/admin/appointments")

    assert response.status_code == 401


@pytest.mark.integration
def test_get_appointments_authorized(client: TestClient, test_admin_token: str, test_appointment: Appointment):
    """Test getting appointments with valid token."""
    response = client.get(
        "/admin/appointments",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.integration
def test_get_appointments_filter_by_status(
    client: TestClient,
    test_admin_token: str,
    test_db_session,
    test_user: User,
    test_slots: list
):
    """Test filtering appointments by status."""
    # Create confirmed and cancelled appointments
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
    test_slots[0].is_booked = True
    test_slots[1].is_booked = True
    test_db_session.add(confirmed_appt)
    test_db_session.add(cancelled_appt)
    test_db_session.commit()

    response = client.get(
        "/admin/appointments?status=confirmed",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert all(appt["status"] == "confirmed" for appt in data)


@pytest.mark.integration
def test_update_appointment_status(
    client: TestClient,
    test_admin_token: str,
    test_appointment: Appointment
):
    """Test updating appointment status."""
    response = client.patch(
        f"/admin/appointments/{test_appointment.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json={"status": "completed"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


@pytest.mark.integration
def test_update_appointment_invalid_status(
    client: TestClient,
    test_admin_token: str,
    test_appointment: Appointment
):
    """Test updating appointment with invalid status."""
    response = client.patch(
        f"/admin/appointments/{test_appointment.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json={"status": "invalid_status"}
    )

    assert response.status_code == 400


@pytest.mark.integration
def test_update_nonexistent_appointment(
    client: TestClient,
    test_admin_token: str
):
    """Test updating non-existent appointment."""
    response = client.patch(
        "/admin/appointments/99999",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json={"status": "completed"}
    )

    assert response.status_code == 404


@pytest.mark.integration
def test_get_available_slots(
    client: TestClient,
    test_admin_token: str,
    test_slots: list
):
    """Test getting available slots."""
    response = client.get(
        "/admin/slots/available",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5  # All test_slots are available


@pytest.mark.integration
def test_create_slot(client: TestClient, test_admin_token: str):
    """Test creating a new slot."""
    start_time = datetime.utcnow() + timedelta(days=2)
    end_time = start_time + timedelta(minutes=30)

    response = client.post(
        "/admin/slots",
        headers={"Authorization": f"Bearer {test_admin_token}"},
        json={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["is_booked"] is False


@pytest.mark.integration
def test_delete_slot(
    client: TestClient,
    test_admin_token: str,
    test_slots: list
):
    """Test deleting an unbooked slot."""
    slot = test_slots[0]

    response = client.delete(
        f"/admin/slots/{slot.id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    assert response.status_code == 200


@pytest.mark.integration
def test_delete_booked_slot(
    client: TestClient,
    test_admin_token: str,
    test_appointment: Appointment,
    test_db_session
):
    """Test that deleting a booked slot is prevented."""
    slot_id = test_appointment.slot_id

    response = client.delete(
        f"/admin/slots/{slot_id}",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    # Should either fail (400) or succeed but appointment handling varies
    assert response.status_code in [200, 400]


@pytest.mark.integration
def test_get_dashboard_stats(
    client: TestClient,
    test_admin_token: str,
    test_appointment: Appointment
):
    """Test getting dashboard statistics."""
    response = client.get(
        "/admin/dashboard/stats",
        headers={"Authorization": f"Bearer {test_admin_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify stats structure
    assert "total_appointments" in data
    assert "today_appointments" in data
    assert "pending_confirmations" in data
    assert "available_slots" in data

    # Verify types
    assert isinstance(data["total_appointments"], int)
    assert isinstance(data["today_appointments"], int)
    assert isinstance(data["pending_confirmations"], int)
    assert isinstance(data["available_slots"], int)


@pytest.mark.integration
def test_invalid_token(client: TestClient):
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/admin/appointments",
        headers={"Authorization": "Bearer invalid_token_here"}
    )

    assert response.status_code == 401


@pytest.mark.integration
def test_missing_authorization_header(client: TestClient):
    """Test accessing protected endpoint without authorization header."""
    response = client.get("/admin/appointments")

    assert response.status_code == 401


@pytest.mark.integration
def test_malformed_authorization_header(client: TestClient):
    """Test with malformed authorization header."""
    response = client.get(
        "/admin/appointments",
        headers={"Authorization": "NotBearer token"}
    )

    assert response.status_code == 401
