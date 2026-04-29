#!/usr/bin/env python
"""Test admin API endpoints."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
from datetime import datetime, timedelta


BASE_URL = "http://localhost:8000"


def test_login():
    """Test admin login and get token."""
    print("🔐 Testing admin login...")

    response = requests.post(
        f"{BASE_URL}/admin/auth/login",
        json={
            "username": "barber",
            "password": "barber123"  # Use your actual password
        }
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Login successful!")
        print(f"   Token: {data['access_token'][:50]}...")
        print(f"   Expires in: {data['expires_in']} seconds")
        return data['access_token']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   {response.json()}")
        return None


def test_get_admin_info(token):
    """Test getting current admin info."""
    print("\n👤 Testing get admin info...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/auth/me",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Got admin info:")
        print(f"   Username: {data['username']}")
        print(f"   ID: {data['id']}")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.json()}")


def test_get_stats(token):
    """Test getting dashboard stats."""
    print("\n📊 Testing dashboard stats...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/stats",
        headers=headers
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Stats retrieved:")
        print(f"   Today's appointments: {data['today_appointments']}")
        print(f"   Pending confirmations: {data['pending_confirmations']}")
        print(f"   Available slots: {data['available_slots']}")
        print(f"   Total customers: {data['total_customers']}")
    else:
        print(f"❌ Failed: {response.status_code}")


def test_get_slots(token):
    """Test getting available slots."""
    print("\n📅 Testing get slots...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/slots",
        headers=headers,
        params={"available_only": True}
    )

    if response.status_code == 200:
        slots = response.json()
        print(f"✅ Retrieved {len(slots)} available slots")
        if slots:
            print(f"   First slot: {slots[0]['start_time']}")
    else:
        print(f"❌ Failed: {response.status_code}")


def test_create_slot(token):
    """Test creating a new slot."""
    print("\n➕ Testing create slot...")

    headers = {"Authorization": f"Bearer {token}"}

    # Create slot for tomorrow at 2pm
    tomorrow = datetime.now() + timedelta(days=1)
    start = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    end = start + timedelta(minutes=30)

    response = requests.post(
        f"{BASE_URL}/admin/slots",
        headers=headers,
        json={
            "start_time": start.isoformat(),
            "end_time": end.isoformat()
        }
    )

    if response.status_code == 201:
        data = response.json()
        print(f"✅ Slot created:")
        print(f"   ID: {data['id']}")
        print(f"   Time: {data['start_time']}")
        return data['id']
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   {response.json()}")
        return None


def test_get_appointments(token):
    """Test getting appointments."""
    print("\n📋 Testing get appointments...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/admin/appointments",
        headers=headers
    )

    if response.status_code == 200:
        appointments = response.json()
        print(f"✅ Retrieved {len(appointments)} appointments")
        if appointments:
            appt = appointments[0]
            print(f"   Example: {appt['customer_phone']} at {appt['start_time']}")
            print(f"   Status: {appt['status']}")
            return appt['id']
    else:
        print(f"❌ Failed: {response.status_code}")
    return None


def test_update_appointment(token, appointment_id):
    """Test updating appointment status."""
    if not appointment_id:
        print("\n⏭️  Skipping update appointment (no appointment ID)")
        return

    print(f"\n📝 Testing update appointment {appointment_id}...")

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.patch(
        f"{BASE_URL}/admin/appointments/{appointment_id}",
        headers=headers,
        json={"status": "completed"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Appointment updated:")
        print(f"   Status: {data['status']}")
    else:
        print(f"❌ Failed: {response.status_code}")


def test_unauthenticated_access():
    """Test accessing protected route without token."""
    print("\n🚫 Testing unauthorized access...")

    response = requests.get(f"{BASE_URL}/admin/stats")

    if response.status_code == 401 or response.status_code == 403:
        print(f"✅ Correctly rejected (status {response.status_code})")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ADMIN API TESTS")
    print("=" * 60)
    print("\nMake sure the server is running:")
    print("  uvicorn app.main:app --reload\n")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        sys.exit(1)

    # Run tests
    token = test_login()
    if not token:
        print("\n❌ Cannot proceed without token")
        sys.exit(1)

    test_get_admin_info(token)
    test_get_stats(token)
    test_get_slots(token)
    slot_id = test_create_slot(token)
    appointment_id = test_get_appointments(token)
    test_update_appointment(token, appointment_id)
    test_unauthenticated_access()

    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
