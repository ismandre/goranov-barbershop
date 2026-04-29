# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Goranov Barbershop is a WhatsApp-based virtual assistant for managing barbershop appointments. The system consists of:
- **WhatsApp Bot** (via Twilio) for customers to book/manage appointments
- **FastAPI Backend** with state machine for conversation flow
- **SQLite Database** for persistence
- **Admin Dashboard** (planned) for barber to manage availability

Primary language: Croatian (messages to customers are in Croatian).

## Architecture

### Request Flow
```
WhatsApp (Customer)
  → Twilio Webhook
  → FastAPI (/whatsapp/webhook)
  → Message Processor
  → State Machine
  → Database
  → Response back to WhatsApp
```

### State Machine Pattern

The core of the bot is a **finite state machine** with two main components:

1. **States** (`state_machine/states/`) - Represent current conversation position
   - Each state extends `State` base class
   - Implement `on_action(action: Action) -> State` method
   - Return next state based on action received
   - Examples: `StateUserUnknown`, `StateMainMenu`, `StateShowAvailableAppointments`

2. **Actions** (`state_machine/actions/`) - Represent user intents
   - Each action extends `Action` base class
   - Defined in `ActionType` enum
   - Examples: `ActionUserMessage`, `ActionShowAvailableAppointments`, `ActionBookAppointment`

**Pattern**: `current_state.on_action(parsed_action) -> next_state`

### Database Layer

Uses SQLAlchemy ORM with 6 tables:
- `users` - Customer info (phone as unique identifier)
- `user_states` - Tracks conversation state per user
- `available_slots` - Bookable time slots
- `appointments` - Links users to slots
- `admins` - System administrators
- `conversation_history` - Message logs

**Access pattern**:
```python
from app.database import get_db, User, Appointment

with get_db() as db:
    user = db.query(User).filter(User.phone_number == phone).first()
```

### Current vs Target Architecture

**Current state** (`app/logic/state_machine.py`):
- In-memory dictionary storing user states
- Simple hardcoded responses
- **NOT yet integrated with the state machine in `state_machine/`**

**Target state**:
- Use database for state persistence
- Use the full state machine in `state_machine/` directory
- Parse user messages to determine actions (intent recognition)
- Store conversation history

## Development Commands

### Database Setup
```bash
# Initialize database (creates barbershop.db)
python scripts/init_database.py

# Create admin user
python scripts/create_admin.py

# Seed test time slots (Mon-Fri, 9AM-5PM, next 7 days)
python scripts/seed_slots.py

# Test database operations
python scripts/test_database.py
```

### Running the Application
```bash
# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
uvicorn app.main:app --reload

# Server runs on http://localhost:8000
# Twilio webhook endpoint: POST /whatsapp/webhook
```

### Testing State Machine Locally
```bash
# Run state machine test flow
python state_machine/main.py
```

## Key Files

- `DESIGN.md` - Comprehensive system design document with architecture, API design, implementation plan
- `DATABASE.md` - Database setup and operations guide
- `assets/img/user_flow.jpeg` - Visual state machine flow diagram
- `app/main.py` - FastAPI webhook entry point
- `app/database/models.py` - SQLAlchemy models
- `state_machine/` - State machine implementation (to be integrated)
- `.env.example` - Environment variable template

## Critical Implementation Notes

### State Machine Integration
The `state_machine/` directory contains a complete state machine implementation that is **NOT yet connected** to the FastAPI webhook handler. Current integration TODO:
1. Replace in-memory `USER_STATES` dict in `app/logic/state_machine.py` with database queries
2. Parse incoming WhatsApp messages to determine `Action` type
3. Load user's current state from `user_states` table
4. Call `state.on_action(action)` to get next state
5. Save new state to database
6. Generate appropriate Croatian response based on state

### Message Intent Recognition
Currently missing. Need to parse user messages to actions:
- Keywords: "available", "book" → `ActionShowAvailableAppointments`
- Keywords: "my", "reservations" → `ActionShowExistingReservations`
- Numbers (1, 2, 3) → `ActionSelectAppointment`
- "yes", "da", "continue" → `ActionContinue`
- "no", "ne", "cancel" → `ActionCancel`

### User State Persistence
Each user has ONE active state in `user_states` table with:
- `current_state`: Class name (e.g., "StateMainMenu")
- `context`: JSON string for additional data (selected appointment ID, etc.)

On new message:
1. Look up user by `phone_number` (create if not exists)
2. Get/create `UserState` for user
3. Instantiate state class from `current_state` string
4. Process action and transition
5. Update `user_states.current_state` and `context`

### Twilio Integration
- Webhook receives form data: `From` (phone), `Body` (message)
- Must return TwiML XML response
- Signature validation should be added for production (see Twilio docs)

### Croatian Language
All bot responses must be in Croatian. Message templates should be in a constants file or database table for easy updates.

## Environment Configuration

Required environment variables (see `.env.example`):
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- `DATABASE_URL` (defaults to `sqlite:///./barbershop.db`)
- `JWT_SECRET_KEY` (for admin dashboard auth)
- `TIMEZONE` (defaults to `Europe/Zagreb`)

## Design Decisions

- **SQLite**: Simple, file-based, sufficient for single-barber shop
- **30-minute slots**: Fixed duration (may be configurable later)
- **Keyword matching**: Initial intent recognition (can upgrade to Claude API/NLU later)
- **Stateless webhook**: Each request is independent; state loaded from database
- **Phone number as user ID**: WhatsApp phone from Twilio is the unique identifier

## Implementation Phases

Per `DESIGN.md`, the project is being built in phases:
- **Phase 1** (current): Core backend, state machine, database integration
- **Phase 2**: Admin API endpoints with authentication
- **Phase 3**: Admin dashboard UI
- **Phase 4**: Testing and refinement
- **Phase 5**: Deployment

See `DESIGN.md` for complete implementation plan and technical specifications.
