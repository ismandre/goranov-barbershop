"""Service layer for user-related operations."""

from datetime import datetime
from typing import Optional, Dict, Any
import json

from sqlalchemy.orm import Session

from app.database.models import User, UserState, ConversationHistory
from app.logging_config import get_logger

logger = get_logger(__name__)


class UserService:
    """Handle user and user state operations."""

    @staticmethod
    def get_or_create_user(db: Session, phone_number: str) -> User:
        """Get existing user or create new one."""
        user = db.query(User).filter(User.phone_number == phone_number).first()

        if not user:
            user = User(phone_number=phone_number)
            db.add(user)
            db.commit()
            db.refresh(user)

        # Update last interaction
        user.last_interaction = datetime.utcnow()
        db.commit()

        return user

    @staticmethod
    def get_user_state(db: Session, user_id: int) -> Optional[UserState]:
        """Get user's current state."""
        return db.query(UserState).filter(UserState.user_id == user_id).first()

    @staticmethod
    def set_user_state(
        db: Session,
        user_id: int,
        state_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> UserState:
        """Set or update user's state."""
        user_state = db.query(UserState).filter(UserState.user_id == user_id).first()

        context_json = json.dumps(context) if context else None

        if user_state:
            user_state.current_state = state_name
            user_state.context = context_json
            user_state.updated_at = datetime.utcnow()
        else:
            user_state = UserState(
                user_id=user_id,
                current_state=state_name,
                context=context_json
            )
            db.add(user_state)

        db.commit()
        db.refresh(user_state)
        return user_state

    @staticmethod
    def get_state_context(user_state: Optional[UserState]) -> Dict[str, Any]:
        """Parse context JSON from user state."""
        if not user_state or not user_state.context:
            return {}

        try:
            return json.loads(user_state.context)
        except json.JSONDecodeError as e:
            logger.error(
                f"Failed to parse user state context JSON",
                exc_info=True,
                extra={
                    "user_id": user_state.user_id if user_state else None,
                    "context_value": user_state.context if user_state else None
                }
            )
            return {}

    @staticmethod
    def log_message(
        db: Session,
        user_id: int,
        message: str,
        is_from_user: bool
    ) -> ConversationHistory:
        """Log a conversation message."""
        history = ConversationHistory(
            user_id=user_id,
            message=message,
            is_from_user=is_from_user
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
