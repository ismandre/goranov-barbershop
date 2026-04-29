# Testing Guide - Goranov Barbershop

Quick reference for testing and understanding the WhatsApp bot flow.

## Quick Start Testing

```bash
# 1. Setup (first time only)
python scripts/init_database.py
python scripts/create_admin.py
python scripts/seed_slots.py

# 2. Run automated tests
python tests/test_state_machine.py

# 3. Start server for manual testing
uvicorn app.main:app --reload
```

---

## Understanding the Flow

### Complete Conversation Example

```
User: "Bok!"
  → StateUserUnknown → StateMainMenu
  → Bot: Welcome message + menu (1️⃣ Rezerviraj termin, 2️⃣ Moje rezervacije)

User: "1"
  → StateMainMenu → StateShowAvailableAppointments
  → Bot: List of available slots (1️⃣, 2️⃣, 3️⃣...)

User: "1"
  → StateShowAvailableAppointments → StateAppointmentSelected
  → Bot: "Želite li potvrditi termin: [date/time]?"

User: "da"
  → StateAppointmentSelected → StateIdle (appointment booked!)
  → Bot: "Termin je potvrđen! ✅"
```

### State Machine Flow

```
USER_DOES_NOT_EXIST
  ↓ (any message)
StateUserUnknown
  ↓ (ACTION_USER_MESSAGE)
StateMainMenu
  ├─→ "1" (ACTION_SHOW_AVAILABLE_APPOINTMENTS) → StateShowAvailableAppointments
  └─→ "2" (ACTION_SHOW_EXISTING_RESERVATIONS) → StateShowMyReservations

StateShowAvailableAppointments
  ↓ (number: ACTION_SELECT_APPOINTMENT)
StateAppointmentSelected
  ↓ ("da": ACTION_BOOK_APPOINTMENT)
StateIdle (booked!)
```

### Intent Recognition

| User Input | Current State | Parsed Action |
|------------|---------------|---------------|
| "Bok", "Hello" | Any | ACTION_USER_MESSAGE |
| "1" | StateMainMenu | ACTION_SHOW_AVAILABLE_APPOINTMENTS |
| "2" | StateMainMenu | ACTION_SHOW_EXISTING_RESERVATIONS |
| "1", "2", "3"... | StateShowAvailableAppointments | ACTION_SELECT_APPOINTMENT |
| "da", "yes" | StateAppointmentSelected | ACTION_BOOK_APPOINTMENT |
| "rezerviraj" | StateMainMenu | ACTION_SHOW_AVAILABLE_APPOINTMENTS |
| "moje rezervacije" | StateMainMenu | ACTION_SHOW_EXISTING_RESERVATIONS |

---

## Manual Testing Methods

### Method 1: Automated Test Suite

```bash
python tests/test_state_machine.py
```

**Output shows:**
- Each step of the conversation
- Bot responses
- State transitions
- Success/failure status

### Method 2: curl (Simulates Twilio Webhook)

```bash
# Start server
uvicorn app.main:app --reload

# Test complete flow (run each command in order):

# 1. Welcome
curl -X POST http://localhost:8000/whatsapp/webhook \
  -d "From=whatsapp:+385991234567" \
  -d "Body=Bok"

# 2. Show available slots
curl -X POST http://localhost:8000/whatsapp/webhook \
  -d "From=whatsapp:+385991234567" \
  -d "Body=1"

# 3. Select first slot
curl -X POST http://localhost:8000/whatsapp/webhook \
  -d "From=whatsapp:+385991234567" \
  -d "Body=1"

# 4. Confirm booking
curl -X POST http://localhost:8000/whatsapp/webhook \
  -d "From=whatsapp:+385991234567" \
  -d "Body=da"
```

**Extract just the message text:**
```bash
curl -s -X POST http://localhost:8000/whatsapp/webhook \
  -d "From=whatsapp:+385991234567" \
  -d "Body=Bok" \
  | grep -o '<Message>.*</Message>' | sed 's/<[^>]*>//g'
```

### Method 3: Python Script

Create `manual_test.py`:

```python
#!/usr/bin/env python
"""Manual testing script for conversation flow."""

from app.logic.state_machine import handle_state_transition

def test_booking_flow():
    phone = "+385991234567"

    print("=" * 60)
    print("BOOKING FLOW TEST")
    print("=" * 60)

    # Step 1: Welcome
    print("\n👤 User: Bok!")
    response = handle_state_transition(phone, "Bok")
    print(f"🤖 Bot:\n{response}\n")

    # Step 2: Show slots
    print("👤 User: 1")
    response = handle_state_transition(phone, "1")
    print(f"🤖 Bot:\n{response}\n")

    # Step 3: Select slot
    print("👤 User: 1")
    response = handle_state_transition(phone, "1")
    print(f"🤖 Bot:\n{response}\n")

    # Step 4: Confirm
    print("👤 User: da")
    response = handle_state_transition(phone, "da")
    print(f"🤖 Bot:\n{response}\n")

    print("=" * 60)
    print("✅ Booking flow complete")
    print("=" * 60)

if __name__ == "__main__":
    test_booking_flow()
```

Run it:
```bash
python manual_test.py
```

### Method 4: Interactive Python Shell

```bash
python -i -c "from app.logic.state_machine import handle_state_transition; phone = '+385991234567'"

>>> print(handle_state_transition(phone, "Bok"))
>>> print(handle_state_transition(phone, "1"))
>>> print(handle_state_transition(phone, "1"))
>>> print(handle_state_transition(phone, "da"))
```

---

## Database Verification

### Check What's in the Database

```bash
sqlite3 barbershop.db
```

**Useful queries:**

```sql
-- List all users
SELECT id, phone_number, name, last_interaction FROM users;

-- Check user's current state
SELECT u.phone_number, us.current_state, us.context, us.updated_at
FROM users u
LEFT JOIN user_states us ON u.id = us.user_id
ORDER BY u.last_interaction DESC;

-- View all appointments with details
SELECT
    u.phone_number,
    datetime(s.start_time) as appointment_time,
    a.status,
    a.booked_at
FROM appointments a
JOIN users u ON a.user_id = u.id
JOIN available_slots s ON a.slot_id = s.id
ORDER BY s.start_time DESC;

-- Count appointments by status
SELECT status, COUNT(*) as count
FROM appointments
GROUP BY status;

-- View conversation history
SELECT
    u.phone_number,
    CASE WHEN ch.is_from_user THEN '👤 User' ELSE '🤖 Bot' END as sender,
    ch.message,
    ch.timestamp
FROM conversation_history ch
JOIN users u ON ch.user_id = u.id
ORDER BY ch.timestamp DESC
LIMIT 20;

-- Check available slots
SELECT
    id,
    datetime(start_time) as time,
    is_booked
FROM available_slots
WHERE start_time >= datetime('now')
ORDER BY start_time
LIMIT 10;
```

### Python Database Queries

```python
from app.database import get_db
from app.database.models import User, Appointment, UserState, AvailableSlot

with get_db() as db:
    # Get user by phone
    user = db.query(User).filter(User.phone_number == "+385991234567").first()
    print(f"User: {user.phone_number}, ID: {user.id}")

    # Get user's state
    state = db.query(UserState).filter(UserState.user_id == user.id).first()
    print(f"Current state: {state.current_state}")
    print(f"Context: {state.context}")

    # Get user's appointments
    appointments = db.query(Appointment).filter(Appointment.user_id == user.id).all()
    print(f"Appointments: {len(appointments)}")
    for appt in appointments:
        print(f"  - {appt.status}: {appt.slot.start_time}")

    # Get available slots
    slots = db.query(AvailableSlot).filter(
        AvailableSlot.is_booked == False
    ).limit(5).all()
    print(f"Available slots: {len(slots)}")
```

---

## Common Operations

### Reset Test Data

```bash
# Clean up specific test user
sqlite3 barbershop.db <<EOF
DELETE FROM conversation_history WHERE user_id IN (SELECT id FROM users WHERE phone_number = '+385991234567');
DELETE FROM appointments WHERE user_id IN (SELECT id FROM users WHERE phone_number = '+385991234567');
DELETE FROM user_states WHERE user_id IN (SELECT id FROM users WHERE phone_number = '+385991234567');
DELETE FROM users WHERE phone_number = '+385991234567';
EOF
```

Or use Python:

```python
from app.database import get_db
from app.database.models import User, Appointment, UserState, ConversationHistory

def cleanup_test_user(phone_number: str):
    with get_db() as db:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        if user:
            db.query(ConversationHistory).filter(ConversationHistory.user_id == user.id).delete()
            db.query(Appointment).filter(Appointment.user_id == user.id).delete()
            db.query(UserState).filter(UserState.user_id == user.id).delete()
            db.delete(user)
            db.commit()
            print(f"✅ Cleaned up {phone_number}")

cleanup_test_user("+385991234567")
```

### Reset Entire Database

```bash
rm barbershop.db
python scripts/init_database.py
python scripts/create_admin.py
python scripts/seed_slots.py
```

### Add More Test Slots

```bash
# Add slots for specific date
python scripts/seed_slots.py --date 2024-12-10 --start-hour 9 --end-hour 17

# Add slots for next week (Mon-Fri)
python scripts/seed_slots.py
```

### Check Slot Availability

```sql
-- How many slots available?
SELECT COUNT(*) FROM available_slots WHERE is_booked = 0 AND start_time >= datetime('now');

-- Free up a booked slot
UPDATE available_slots SET is_booked = 0 WHERE id = 1;
```

---

## Troubleshooting

### Issue: No available slots shown

**Check:**
```sql
SELECT COUNT(*) FROM available_slots;
```

**Fix:**
```bash
python scripts/seed_slots.py
```

### Issue: Slots are in the past

**Check:**
```sql
SELECT datetime(start_time) FROM available_slots ORDER BY start_time LIMIT 5;
```

**Fix:** Delete old slots and seed new ones:
```sql
DELETE FROM available_slots WHERE start_time < datetime('now');
```
```bash
python scripts/seed_slots.py
```

### Issue: User stuck in a state

**Check:**
```sql
SELECT u.phone_number, us.current_state, us.context
FROM user_states us
JOIN users u ON us.user_id = u.id
WHERE u.phone_number = '+385991234567';
```

**Fix:** Delete user state (will restart conversation):
```sql
DELETE FROM user_states WHERE user_id = (SELECT id FROM users WHERE phone_number = '+385991234567');
```

### Issue: Import errors

**Fix:**
```bash
# Make sure you're in project root
cd /Users/andreism/me/goranov-barbershop

# Use python -m to run scripts
python -m app.main

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/Users/andreism/me/goranov-barbershop"
```

### Issue: Database locked

**Fix:**
```bash
# Close any open SQLite connections
# Restart the server
# Check no other processes are using the DB
lsof barbershop.db
```

---

## Understanding State Persistence

### How State is Saved

After each message:
1. **Load** user and current state from DB
2. **Parse** message → determine action
3. **Execute** state transition
4. **Generate** response
5. **Save** new state + context to DB
6. **Log** message in conversation_history

### Context JSON Structure

```json
{
  "first_time": true,                    // New user flag
  "available_slots": [1, 2, 3, 4, 5],   // Slot IDs shown to user
  "selected_slot_id": 3                  // Slot user chose
}
```

Context is cleared after successful booking.

---

## Message Templates Reference

All messages are in `app/logic/messages.py`:

| Message | Trigger |
|---------|---------|
| `welcome()` | First-time user |
| `main_menu()` | Return to menu |
| `show_available_slots(slots)` | View slots |
| `confirm_booking(slot)` | Slot selected |
| `booking_confirmed(slot)` | Booking successful |
| `show_my_reservations(appointments)` | View reservations |
| `no_reservations()` | No active appointments |
| `invalid_choice()` | Invalid input |
| `error()` | Generic error |

Croatian date format: "Ponedjeljak, 5. prosinca 2024."

---

## Testing Checklist

Before considering flow complete, verify:

- [ ] New user gets welcome message
- [ ] Main menu shows two options
- [ ] Selecting "1" shows available slots
- [ ] Slots are properly formatted (Croatian date/time)
- [ ] Selecting a slot shows confirmation
- [ ] Confirming creates appointment in DB
- [ ] Appointment marks slot as booked
- [ ] User state is updated correctly
- [ ] Conversation is logged
- [ ] Can start new conversation after booking
- [ ] Invalid inputs show error messages
- [ ] No available slots shows appropriate message

---

## Quick Commands Cheat Sheet

```bash
# Start server
uvicorn app.main:app --reload

# Run tests
python tests/test_state_machine.py

# Test flow manually
python manual_test.py  # (create this from examples above)

# Check database
sqlite3 barbershop.db "SELECT * FROM users;"

# Clean test user
sqlite3 barbershop.db "DELETE FROM users WHERE phone_number = '+385991234567';"

# Add slots
python scripts/seed_slots.py

# Reset everything
rm barbershop.db && python scripts/init_database.py && python scripts/seed_slots.py

# Check server health
curl http://localhost:8000/

# Simulate message
curl -X POST http://localhost:8000/whatsapp/webhook -d "From=whatsapp:+385991234567" -d "Body=Bok"
```

---

## Next: Connecting to Real WhatsApp

When ready to test with actual WhatsApp:

1. **Get Twilio account** (https://www.twilio.com)
2. **Configure Twilio WhatsApp Sandbox**
3. **Set webhook URL** to your server: `https://yourdomain.com/whatsapp/webhook`
4. **Send message** from your phone to Twilio number
5. **See it work!** 🎉

For local testing with real WhatsApp, use ngrok:
```bash
# Start ngrok
ngrok http 8000

# Use the HTTPS URL in Twilio webhook settings
# Example: https://abc123.ngrok.io/whatsapp/webhook
```

---

**Last Updated**: 2024-04-29
**Phase**: 1 Complete - Core Backend Integration ✅
