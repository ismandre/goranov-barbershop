from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class User(Base):
    """Customer/user who interacts with the WhatsApp bot."""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_interaction = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    state = relationship("UserState", back_populates="user", uselist=False)
    appointments = relationship("Appointment", back_populates="user")
    conversation_history = relationship("ConversationHistory", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone_number}, name={self.name})>"


class UserState(Base):
    """Current state of user in the conversation flow."""
    __tablename__ = 'user_states'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True, index=True)
    current_state = Column(String(100), nullable=False)
    context = Column(Text, nullable=True)  # JSON string for additional context
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="state")

    def __repr__(self):
        return f"<UserState(user_id={self.user_id}, state={self.current_state})>"


class AvailableSlot(Base):
    """Time slots available for booking."""
    __tablename__ = 'available_slots'

    id = Column(Integer, primary_key=True, autoincrement=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    is_booked = Column(Boolean, default=False, nullable=False)
    created_by = Column(Integer, ForeignKey('admins.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    admin = relationship("Admin", back_populates="created_slots")
    appointment = relationship("Appointment", back_populates="slot", uselist=False)

    def __repr__(self):
        return f"<AvailableSlot(id={self.id}, start={self.start_time}, booked={self.is_booked})>"


class Appointment(Base):
    """Booked appointments linking users to slots."""
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    slot_id = Column(Integer, ForeignKey('available_slots.id'), nullable=False, index=True)
    status = Column(String(20), nullable=False, default='pending')  # pending, confirmed, completed, cancelled, no_show
    booked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="appointments")
    slot = relationship("AvailableSlot", back_populates="appointment")

    def __repr__(self):
        return f"<Appointment(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Admin(Base):
    """Admin users (barbers) who manage the system."""
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    created_slots = relationship("AvailableSlot", back_populates="admin")

    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username})>"


class ConversationHistory(Base):
    """Log of all messages exchanged with users."""
    __tablename__ = 'conversation_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    message = Column(Text, nullable=False)
    is_from_user = Column(Boolean, nullable=False)  # True if from customer, False if from bot
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="conversation_history")

    def __repr__(self):
        direction = "User" if self.is_from_user else "Bot"
        return f"<ConversationHistory({direction}: {self.message[:50]})>"
