# Goranov Barbershop - System Design Document

## 1. Product Overview

### 1.1 Purpose
A WhatsApp-based virtual assistant for managing barbershop appointments, allowing customers to book slots and the barber to manage availability through a dashboard.

### 1.2 Core Users
- **Customers**: Book appointments via WhatsApp
- **Barber (Admin)**: Manage availability and view appointments via web dashboard

### 1.3 Key Features

#### Customer Features (WhatsApp Bot)
- View available appointment slots
- Book appointments
- View their existing reservations
- Cancel/modify reservations
- Natural conversational flow

#### Barber Features (Admin Dashboard)
- View daily/weekly appointment schedule
- Add new available time slots
- Block out unavailable times
- View appointment details (customer info, time, status)
- Mark appointments as completed/no-show

---

## 2. User Flows

### 2.1 Customer Journey (from user_flow.jpeg)

```
USER DOES NOT EXIST
  ↓ (user sends message)
AT MAIN MENU
  ├─→ list my reservations (my_reservations > 0)
  │   ↓
  │   LISTED MY RESERVATIONS
  │   ├─→ cancel → PROMPT LIST MY RESERVATIONS → (cancel) → APPOINTMENT SELECTED
  │   └─→ continue → APPOINTMENT SELECTED
  │
  └─→ list my reservations (my_reservations = 0)
      ↓
      LISTED MY EMPTY RESERVATIONS
      ├─→ continue → PROMPT LIST MY EMPTY RESERVATIONS
      │   ├─→ cancel → APPOINTMENT SELECTED
      │   └─→ continue → APPOINTMENT SELECTED
      │
      └─→ list available reservations
          ↓
          LISTED APPOINTMENTS AVAILABLE
          ├─→ continue → PROMPT LISTED APPOINTMENTS AVAILABLE
          │   └─→ continue → APPOINTMENT SELECTED
          │       ├─→ picked appointment → APPOINTMENT SELECTED
          │       │   └─→ continue → PROMPT PICKED APPOINTMENT
          │       │       ├─→ cancel → APPOINTMENT SELECTED
          │       │       └─→ continue → NO FLOW STARTED (successful booking)
          │       └─→ * → APPOINTMENT SELECTED
          └─→ * → LISTED APPOINTMENTS AVAILABLE
```

### 2.2 State Flow Description

1. **Initial Contact**: New user sends first message
2. **Main Menu**: User chooses to see available appointments or their reservations
3. **View Reservations Path**:
   - If user has reservations: show list, allow cancel/continue
   - If no reservations: prompt to book new appointment
4. **Booking Path**:
   - Show available appointments
   - User selects appointment
   - Confirm selection
   - Book appointment
5. **End State**: Return to idle or main menu

---

## 3. Architecture Design

### 3.1 System Architecture

```
┌─────────────┐
│   WhatsApp  │
│   Customer  │
└──────┬──────┘
       │ HTTP POST
       ↓
┌─────────────────────────────┐
│      Twilio Platform        │
│  (WhatsApp Business API)    │
└──────┬──────────────────────┘
       │ Webhook
       ↓
┌─────────────────────────────┐
│   FastAPI Backend           │
│  ┌─────────────────────┐    │
│  │ Twilio Webhook      │    │
│  │ Handler             │    │
│  └─────┬───────────────┘    │
│        ↓                    │
│  ┌─────────────────────┐    │
│  │ Message Processor   │    │
│  │ (NLU/Intent)        │    │
│  └─────┬───────────────┘    │
│        ↓                    │
│  ┌─────────────────────┐    │
│  │ State Machine       │    │
│  │ Engine              │    │
│  └─────┬───────────────┘    │
│        ↓                    │
│  ┌─────────────────────┐    │
│  │ Business Logic      │    │
│  │ (Appointments,      │    │
│  │  Availability)      │    │
│  └─────┬───────────────┘    │
│        ↓                    │
│  ┌─────────────────────┐    │
│  │ SQLite Database     │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
       ↑
       │ HTTPS
       ↓
┌─────────────────────────────┐
│   Admin Dashboard           │
│   (Web Interface)           │
│  ┌─────────────────────┐    │
│  │ React/HTML Frontend │    │
│  └─────────────────────┘    │
└─────────────────────────────┘
```

### 3.2 Technology Stack

**Backend**:
- FastAPI (Python 3.13)
- Twilio SDK for WhatsApp integration
- SQLite (simple, file-based database)
- Uvicorn (ASGI server)

**Frontend (Admin Dashboard)**:
- Option 1: Simple HTML/CSS/JavaScript (lightweight)
- Option 2: React (more scalable)
- Option 3: Server-side rendering with Jinja2 templates

**Infrastructure**:
- Deployment: Railway / Render / Heroku / VPS
- Database: SQLite file (stored in persistent volume)

---

## 4. Database Schema

### 4.1 Tables

#### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone_number TEXT UNIQUE NOT NULL,  -- WhatsApp number (from Twilio)
    name TEXT,                          -- Optional: extracted from conversation
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### User States Table
```sql
CREATE TABLE user_states (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    current_state TEXT NOT NULL,        -- State machine state name
    context JSON,                       -- Additional state context (selected appointment, etc.)
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id)                     -- Only one active state per user
);
```

#### Available Slots Table
```sql
CREATE TABLE available_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    is_booked BOOLEAN DEFAULT FALSE,
    created_by INTEGER,                 -- Admin who created the slot
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES admins(id)
);
```

#### Appointments Table
```sql
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    slot_id INTEGER NOT NULL,
    status TEXT NOT NULL,               -- 'pending', 'confirmed', 'completed', 'cancelled', 'no_show'
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,                         -- Optional notes from customer
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (slot_id) REFERENCES available_slots(id)
);
```

#### Admins Table
```sql
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,        -- Hashed password
    phone_number TEXT,                  -- Barber's phone
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Conversation History Table (Optional)
```sql
CREATE TABLE conversation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_from_user BOOLEAN NOT NULL,      -- TRUE if from customer, FALSE if from bot
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 4.2 Indexes
```sql
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_appointments_user ON appointments(user_id);
CREATE INDEX idx_appointments_slot ON appointments(slot_id);
CREATE INDEX idx_available_slots_time ON available_slots(start_time);
CREATE INDEX idx_user_states_user ON user_states(user_id);
```

---

## 5. State Machine Design

### 5.1 States (from user_flow.jpeg)

| State | Description | Valid Actions |
|-------|-------------|---------------|
| `StateUserUnknown` | New user, never interacted before | UserMessage → MainMenu |
| `StateMainMenu` | Initial menu presented to user | ShowAvailableAppointments, ShowMyReservations |
| `StateShowAvailableAppointments` | Display list of available slots | SelectAppointment, Cancel |
| `StateAwaitAppointmentSelection` | Waiting for user to pick a slot | SelectAppointment, Cancel |
| `StateAppointmentSelected` | User selected a specific slot | Confirm (BookAppointment), Cancel |
| `StateConfirmAppointment` | Confirming the booking | BookAppointment, Cancel |
| `StateShowMyReservations` | Display user's current bookings | ViewDetails, Cancel, Continue |
| `StateAwaitMyReservationAction` | User viewing their reservations | Cancel, Continue |
| `StateShowNoReservations` | User has no current reservations | Continue (to booking flow), Cancel |
| `StateAwaitNoReservationAction` | After showing no reservations | Continue, Cancel |
| `StateIdle` | User has completed flow, waiting | Any new message → MainMenu |

### 5.2 Actions (from action_type.py)

| Action | Description | Trigger |
|--------|-------------|---------|
| `ActionUserMessage` | User sends any message | Message received from Twilio |
| `ActionShowAvailableAppointments` | Show available slots | User requests to see availability |
| `ActionShowExistingReservations` | Show user's bookings | User requests to see their appointments |
| `ActionShowNoReservations` | Inform no bookings exist | User has 0 reservations |
| `ActionSelectAppointment` | User picks a slot | User responds with slot number/identifier |
| `ActionContinue` | User confirms action | User says "continue", "yes", "proceed" |
| `ActionCancel` | User cancels operation | User says "cancel", "no", "back" |
| `ActionBookAppointment` | Finalize booking | After confirmation |

### 5.3 State Transition Logic

The state machine follows this pattern:
```python
current_state = get_user_state(user_id)
action = parse_user_message(message)  # NLU/Intent recognition
next_state = current_state.on_action(action)
save_user_state(user_id, next_state)
response = generate_response(next_state, context)
```

### 5.4 Message Intent Recognition

For simplicity, use keyword matching initially:
- **Show availability**: "available", "book", "appointment", "schedule"
- **My reservations**: "my", "reservations", "bookings", "appointments"
- **Select appointment**: Numbers (1, 2, 3) or time strings
- **Continue**: "yes", "continue", "proceed", "da", "nastavi"
- **Cancel**: "no", "cancel", "back", "ne", "odustani"

Future: Integrate Claude API or simple NLU library for better intent recognition.

---

## 6. API Design

### 6.1 Webhook Endpoint (Twilio → Backend)

**POST /whatsapp/webhook**
```
Headers:
  Content-Type: application/x-www-form-urlencoded

Body (Form data from Twilio):
  From: whatsapp:+1234567890
  To: whatsapp:+0987654321
  Body: "I want to book an appointment"
  MessageSid: SM123456789

Response:
  Content-Type: application/xml
  Body: TwiML response with message
```

### 6.2 Admin API Endpoints

**Authentication**:
```
POST /admin/login
  Body: { "username": "barber", "password": "..." }
  Response: { "token": "jwt_token" }
```

**Appointments**:
```
GET /admin/appointments
  Query: ?date=2024-12-05&status=pending
  Response: [
    {
      "id": 1,
      "customer_phone": "+1234567890",
      "customer_name": "John",
      "start_time": "2024-12-05T10:00:00",
      "end_time": "2024-12-05T10:30:00",
      "status": "confirmed"
    }
  ]

PATCH /admin/appointments/{id}
  Body: { "status": "completed" }
  Response: { "success": true }
```

**Available Slots**:
```
GET /admin/slots
  Query: ?date=2024-12-05
  Response: [
    {
      "id": 1,
      "start_time": "2024-12-05T10:00:00",
      "end_time": "2024-12-05T10:30:00",
      "is_booked": false
    }
  ]

POST /admin/slots
  Body: {
    "start_time": "2024-12-05T10:00:00",
    "end_time": "2024-12-05T10:30:00"
  }
  Response: { "id": 1, "success": true }

POST /admin/slots/bulk
  Body: {
    "date": "2024-12-05",
    "slots": [
      { "start": "09:00", "end": "09:30" },
      { "start": "09:30", "end": "10:00" },
      ...
    ]
  }
  Response: { "created": 10 }

DELETE /admin/slots/{id}
  Response: { "success": true }
```

**Dashboard Stats**:
```
GET /admin/stats
  Response: {
    "today_appointments": 5,
    "pending_confirmations": 2,
    "available_slots": 8,
    "total_customers": 120
  }
```

---

## 7. Admin Dashboard Design

### 7.1 Pages

1. **Login Page**
   - Username/password form
   - Session-based or JWT authentication

2. **Dashboard (Home)**
   - Today's appointments (timeline view)
   - Quick stats (total appointments, pending, completed)
   - Next appointment highlighted

3. **Calendar View**
   - Weekly/monthly calendar
   - Color-coded appointments (pending, confirmed, completed)
   - Click appointment to view details

4. **Manage Availability**
   - Add single slot (date, start time, end time)
   - Bulk add slots (e.g., Mon-Fri 9AM-5PM, 30min intervals)
   - Delete/block slots
   - View all available slots

5. **Appointments List**
   - Filterable by date, status
   - Customer info, time, actions (mark completed, cancel)

6. **Customer List (Optional)**
   - View all customers
   - See their booking history
   - Contact info

### 7.2 UI Mockup Structure

```
┌─────────────────────────────────────────────┐
│  Goranov Barbershop - Admin Dashboard      │
├─────────────────────────────────────────────┤
│  [Dashboard] [Calendar] [Availability]      │
│                                    [Logout] │
├─────────────────────────────────────────────┤
│                                             │
│  Today: Dec 5, 2024                         │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ 09:00 - 09:30  ✓ John Doe             │ │
│  │ 09:30 - 10:00  ⏱  Pending confirmation│ │
│  │ 10:00 - 10:30  [Available]            │ │
│  │ 10:30 - 11:00  ✓ Jane Smith           │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  Stats:                                     │
│  ┌────────┬────────┬──────────┐            │
│  │  5     │   2    │    8     │            │
│  │ Today  │Pending │Available │            │
│  └────────┴────────┴──────────┘            │
└─────────────────────────────────────────────┘
```

---

## 8. Message Templates

### 8.1 Croatian Language Templates

```python
MESSAGES = {
    "welcome": "Bok! 👋 Dobrodošli u Goranov Barbershop. Kako vam mogu pomoći?\n\n1️⃣ Rezerviraj termin\n2️⃣ Moje rezervacije",

    "show_available_slots": "Evo slobodnih termina:\n\n{slots}\n\nOdaberite broj termina koji želite rezervirati.",

    "no_slots_available": "Nažalost, trenutno nema slobodnih termina. Molimo pokušajte kasnije.",

    "confirm_booking": "Želite li potvrditi termin:\n📅 {date}\n🕐 {time}\n\n1️⃣ Potvrdi\n2️⃣ Odustani",

    "booking_confirmed": "Termin je potvrđen! ✅\n📅 {date}\n🕐 {time}\n\nVidimo se! 💈✂️",

    "show_my_reservations": "Vaše rezervacije:\n\n{reservations}\n\n1️⃣ Otkaži rezervaciju\n2️⃣ Natrag na glavni izbornik",

    "no_reservations": "Nemate aktivnih rezervacija.\n\n1️⃣ Rezerviraj termin\n2️⃣ Natrag",

    "cancel_confirmation": "Jeste li sigurni da želite otkazati termin?\n📅 {date}\n🕐 {time}\n\n1️⃣ Da, otkaži\n2️⃣ Ne, zadrži",

    "cancel_success": "Termin je uspješno otkazan. ✅",

    "error": "Nešto nije u redu. Molimo pokušajte ponovno ili kontaktirajte nas.",

    "invalid_choice": "Nevažeći izbor. Molimo pokušajte ponovno."
}
```

---

## 9. Implementation Plan

### 9.1 Phase 1: Core Backend (Week 1-2)

**Tasks**:
1. Set up database schema (SQLite)
2. Create database models (SQLAlchemy or raw SQL)
3. Implement state machine engine
4. Implement all state classes
5. Implement all action classes
6. Create message intent parser
7. Integrate state machine with FastAPI webhook
8. Test basic flow: welcome → show slots → book → confirm

**Deliverables**:
- Working webhook that responds to WhatsApp messages
- State machine correctly transitions between states
- Can book appointments through WhatsApp

### 9.2 Phase 2: Admin API (Week 3)

**Tasks**:
1. Create admin authentication (JWT or session-based)
2. Implement admin API endpoints
   - GET/POST/DELETE slots
   - GET/PATCH appointments
   - GET stats
3. Add password hashing (bcrypt)
4. Test all endpoints with Postman/curl

**Deliverables**:
- Functional REST API for admin operations
- Secure authentication

### 9.3 Phase 3: Admin Dashboard UI (Week 4)

**Tasks**:
1. Choose frontend approach (React vs simple HTML/JS)
2. Build login page
3. Build dashboard/home page
4. Build calendar view
5. Build manage availability page
6. Build appointments list page
7. Connect frontend to backend API

**Deliverables**:
- Working admin dashboard
- Barber can add slots and view appointments

### 9.4 Phase 4: Testing & Refinement (Week 5)

**Tasks**:
1. End-to-end testing with real WhatsApp numbers
2. Handle edge cases:
   - Multiple users at once
   - Invalid inputs
   - Concurrent booking of same slot
   - Network failures
3. Add logging and monitoring
4. Optimize database queries
5. Add conversation history tracking

**Deliverables**:
- Production-ready system
- Comprehensive error handling

### 9.5 Phase 5: Deployment (Week 6)

**Tasks**:
1. Set up deployment environment (Railway/Render)
2. Configure Twilio webhook URL to point to deployed backend
3. Set up persistent storage for SQLite database
4. Configure environment variables
5. Set up SSL/HTTPS
6. Create admin user
7. Train barber on using dashboard

**Deliverables**:
- Live system accessible via WhatsApp
- Admin dashboard accessible via web

---

## 10. Technical Decisions

### 10.1 State Persistence

**Decision**: Store user states in SQLite database
- **Why**: Persistent across server restarts
- **Alternative**: In-memory dictionary (loses state on restart)

### 10.2 Message Processing

**Decision**: Simple keyword-based intent recognition initially
- **Why**: Fast, deterministic, no external API costs
- **Future**: Upgrade to Claude API or Rasa for NLU

### 10.3 Database Choice

**Decision**: SQLite
- **Why**: Simple, file-based, no separate server needed, perfect for single-barber shop
- **Alternative**: PostgreSQL (overkill for this use case)

### 10.4 Frontend Framework

**Decision**: Simple HTML/CSS/JavaScript (or lightweight React)
- **Why**: Faster development, less complexity, sufficient for single-user dashboard
- **Alternative**: Full React app (more scalable but slower to build)

### 10.5 Authentication

**Decision**: JWT tokens for admin API
- **Why**: Stateless, easy to implement, works well with React
- **Alternative**: Session-based (requires server-side session storage)

### 10.6 Appointment Duration

**Decision**: Fixed 30-minute slots
- **Why**: Standardized scheduling, easier to manage
- **Future**: Configurable slot duration

### 10.7 Timezone Handling

**Decision**: Store all times in UTC, convert to local (Croatian time) for display
- **Why**: Avoids daylight saving issues, proper for distributed systems

---

## 11. Security Considerations

1. **Twilio Webhook Validation**:
   - Validate requests are actually from Twilio using signature verification
   - Prevent unauthorized access to webhook endpoint

2. **Admin Authentication**:
   - Secure password hashing (bcrypt with salt)
   - JWT token expiration (e.g., 24 hours)
   - HTTPS only for admin dashboard

3. **SQL Injection Prevention**:
   - Use parameterized queries or ORM
   - Never construct SQL from user input

4. **Rate Limiting**:
   - Prevent spam from WhatsApp users
   - Limit API calls from admin dashboard

5. **Data Privacy**:
   - Store only necessary customer data (phone number)
   - Comply with GDPR if applicable (data deletion requests)

---

## 12. Future Enhancements

1. **Reminders**: Send WhatsApp reminders 24h before appointment
2. **Multi-barber support**: Multiple barbers, each with their own schedule
3. **Payment integration**: Accept deposits/payments via Stripe
4. **Analytics**: Track booking trends, popular times, no-show rates
5. **Multilingual support**: Support English, Croatian, other languages
6. **Voice messages**: Process WhatsApp voice messages for booking
7. **AI-powered chat**: Upgrade to Claude API for more natural conversation
8. **Mobile app**: Native mobile app for barber instead of web dashboard
9. **Waitlist**: Allow customers to join waitlist for sold-out times
10. **Customer preferences**: Store customer haircut preferences/notes

---

## 13. File Structure

```
goranov-barbershop/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Configuration (DB path, Twilio keys, etc.)
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py                # SQLAlchemy models or schema
│   │   ├── connection.py            # DB connection setup
│   │   └── migrations/              # DB migration scripts
│   ├── logic/
│   │   ├── __init__.py
│   │   ├── processor.py             # Message processing entry point
│   │   └── intent_parser.py         # Intent recognition from user messages
│   ├── twilio_handler/
│   │   ├── __init__.py
│   │   ├── client.py                # Twilio client wrapper
│   │   └── validator.py             # Webhook signature validation
│   └── api/
│       ├── __init__.py
│       ├── admin.py                 # Admin API endpoints
│       └── auth.py                  # Authentication endpoints
├── state_machine/
│   ├── __init__.py
│   ├── main.py                      # State machine engine
│   ├── states/
│   │   ├── __init__.py
│   │   ├── state.py                 # Base State class
│   │   ├── state_*.py               # Individual state implementations
│   ├── actions/
│   │   ├── __init__.py
│   │   ├── action.py                # Base Action class
│   │   ├── action_type.py           # Action enum
│   │   └── action_*.py              # Individual action implementations
│   └── context.py                   # State context/session data
├── admin_dashboard/
│   ├── public/
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   └── ...
│   ├── src/
│   │   ├── components/              # React components (if using React)
│   │   ├── services/                # API client
│   │   └── utils/
│   └── package.json                 # If using React/Node
├── tests/
│   ├── test_states.py
│   ├── test_actions.py
│   ├── test_api.py
│   └── test_integration.py
├── scripts/
│   ├── create_admin.py              # Script to create admin user
│   ├── seed_slots.py                # Script to populate initial slots
│   └── migrate_db.py
├── assets/
│   └── img/
│       └── user_flow.jpeg
├── .env                             # Environment variables (not in git)
├── .gitignore
├── requirements.txt
├── README.md
├── DESIGN.md                        # This document
└── LICENSE
```

---

## 14. Environment Variables

```bash
# .env file
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890

DATABASE_URL=sqlite:///./barbershop.db

JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

ADMIN_USERNAME=barber
ADMIN_PASSWORD_HASH=hashed_password

TIMEZONE=Europe/Zagreb
```

---

## 15. Success Metrics

1. **Customer Metrics**:
   - Booking completion rate (% of users who complete booking)
   - Average time to book (from first message to confirmation)
   - Cancellation rate
   - Repeat customer rate

2. **Barber Metrics**:
   - Time saved vs manual booking (minutes per week)
   - Slot utilization rate (% of slots that get booked)
   - No-show rate

3. **Technical Metrics**:
   - Webhook response time (<500ms)
   - System uptime (>99.5%)
   - Error rate (<1%)

---

## 16. Assumptions & Constraints

**Assumptions**:
- Single barber operating the shop
- All appointments are 30 minutes
- Barber works standard hours (e.g., Mon-Fri 9AM-6PM)
- Customers use WhatsApp
- Customers are primarily Croatian-speaking

**Constraints**:
- Twilio WhatsApp API limits (rate limits, message length)
- SQLite limitations (single writer, file locking)
- No payment processing initially
- No SMS fallback (WhatsApp only)

---

## 17. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Twilio API downtime | High | Graceful error messages, retry logic |
| Database corruption | High | Regular backups, use WAL mode |
| Concurrent booking of same slot | Medium | Database transactions, locks |
| Spam/abuse from users | Medium | Rate limiting, block numbers |
| User enters invalid data | Low | Input validation, clear prompts |
| Barber forgets to add slots | Medium | Reminders, bulk slot creation tools |

---

## End of Design Document

**Next Steps**:
1. Review this document with stakeholder (barber)
2. Clarify any ambiguities
3. Begin Phase 1 implementation
4. Set up project tracking (Trello/Linear/GitHub Projects)

**Document Version**: 1.0
**Last Updated**: 2024-12-05
**Author**: Andrei Goranov
