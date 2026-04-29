# Goranov Barbershop - WhatsApp Appointment Bot

A WhatsApp-based virtual assistant for managing barbershop appointments in Croatian.

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_database.py

# Create admin user
python scripts/create_admin.py

# Seed test appointment slots
python scripts/seed_slots.py
```

### 2. Run Server
```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 3. Test
```bash
# Run integration tests
python tests/test_state_machine.py

# Test database operations
python scripts/test_database.py
```

## Features

- 📱 WhatsApp integration via Twilio
- 🇭🇷 Croatian language support
- 📅 View available appointment slots
- ✅ Book appointments
- 📋 View your reservations
- ❌ Cancel appointments
- 💾 SQLite database for persistence
- 🤖 State machine for conversation flow

## Documentation

- `DESIGN.md` - Complete system design and architecture
- `DATABASE.md` - Database setup and operations
- `CLAUDE.md` - Guide for Claude Code instances
- `INTEGRATION_SUMMARY.md` - Integration details and examples

## Project Status

**Phase 1 Complete**: Core backend with state machine integration ✅

Next: Admin API and dashboard (Phase 2)
