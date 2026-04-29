"""Pytest configuration and fixtures for testing."""

import os
from datetime import datetime, timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from faker import Faker

from app.database.models import Base, User, Admin, AvailableSlot, Appointment, UserState, ConversationHistory
from app.database.connection import get_db
from app.main import app
from app.auth.password import hash_password
from app.auth.jwt_handler import create_access_token


# Initialize Faker
fake = Faker()


@pytest.fixture(scope="function")
def test_db_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """Create a new database session for each test with automatic rollback."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(test_db_session):
    """FastAPI test client with database dependency override."""
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(test_db_session: Session) -> User:
    """Create a test user."""
    user = User(
        phone_number="+385991234567",
        name="Test User"
    )
    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(test_db_session: Session) -> Admin:
    """Create a test admin user."""
    admin = Admin(
        username="testadmin",
        password_hash=hash_password("testpass123"),
        phone_number="+385991111111"
    )
    test_db_session.add(admin)
    test_db_session.commit()
    test_db_session.refresh(admin)
    return admin


@pytest.fixture
def test_admin_token(test_admin: Admin) -> str:
    """Generate JWT token for test admin."""
    return create_access_token({"sub": test_admin.username})


@pytest.fixture
def test_slots(test_db_session: Session) -> list:
    """Create 5 available appointment slots for testing."""
    slots = []
    base_time = datetime.utcnow() + timedelta(days=1)

    for i in range(5):
        start_time = base_time + timedelta(hours=i)
        slot = AvailableSlot(
            start_time=start_time,
            end_time=start_time + timedelta(minutes=30),
            is_booked=False
        )
        test_db_session.add(slot)
        slots.append(slot)

    test_db_session.commit()
    for slot in slots:
        test_db_session.refresh(slot)

    return slots


@pytest.fixture
def test_appointment(test_db_session: Session, test_user: User, test_slots: list) -> Appointment:
    """Create a test appointment."""
    slot = test_slots[0]
    slot.is_booked = True

    appointment = Appointment(
        user_id=test_user.id,
        slot_id=slot.id,
        status='confirmed',
        notes='Test appointment'
    )
    test_db_session.add(appointment)
    test_db_session.commit()
    test_db_session.refresh(appointment)
    return appointment


@pytest.fixture
def test_user_state(test_db_session: Session, test_user: User) -> UserState:
    """Create a test user state."""
    user_state = UserState(
        user_id=test_user.id,
        current_state='StateMainMenu',
        context='{}'
    )
    test_db_session.add(user_state)
    test_db_session.commit()
    test_db_session.refresh(user_state)
    return user_state


@pytest.fixture
def test_conversation_history(test_db_session: Session, test_user: User) -> list:
    """Create test conversation history entries."""
    messages = []
    base_time = datetime.utcnow() - timedelta(hours=2)

    for i in range(10):
        msg = ConversationHistory(
            user_id=test_user.id,
            message=f"Test message {i}",
            direction='incoming' if i % 2 == 0 else 'outgoing',
            timestamp=base_time + timedelta(minutes=i * 5)
        )
        test_db_session.add(msg)
        messages.append(msg)

    test_db_session.commit()
    for msg in messages:
        test_db_session.refresh(msg)

    return messages
