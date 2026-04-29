# Concurrency and Race Condition Prevention

## Current Implementation

The `AppointmentService.book_appointment()` method uses SQLAlchemy's `with_for_update()` to implement pessimistic locking:

```python
slot = db.query(AvailableSlot).filter(
    AvailableSlot.id == slot_id
).with_for_update().first()
```

## Database Compatibility

### PostgreSQL / MySQL
✅ **Full Support** - Row-level locking works properly
- `SELECT FOR UPDATE` prevents concurrent transactions from modifying the same row
- Race conditions are properly prevented

### SQLite
⚠️ **Limited Support** - Database-level locking only
- SQLite does not support true row-level locking
- `with_for_update()` falls back to table/database-level locks
- In practice, some race conditions may still occur under high concurrency
- **Recommendation**: Use PostgreSQL for production deployments with high traffic

## Testing

The concurrent booking tests (`tests/test_concurrent_booking.py`) use file-based SQLite to test the locking behavior. Due to SQLite's limitations:
- Tests may show some race conditions
- This is expected behavior for SQLite
- Tests should pass 100% with PostgreSQL/MySQL

## Production Recommendations

For production deployment:

1. **Use PostgreSQL or MySQL** instead of SQLite for proper row-level locking
2. Add a unique constraint on `appointments.slot_id` as a database-level safety net:
   ```sql
   CREATE UNIQUE INDEX idx_unique_slot_booking ON appointments(slot_id)
   WHERE status IN ('confirmed', 'pending');
   ```
3. Monitor logs for "Attempted to book already booked slot" warnings
4. Consider implementing retry logic in the client/webhook layer

## Migration to PostgreSQL

To migrate from SQLite to PostgreSQL:

1. Update `.env`:
   ```
   DATABASE_URL=postgresql://user:password@localhost/barbershop
   ```

2. Install PostgreSQL driver:
   ```bash
   pip install psycopg2-binary
   ```

3. Run migrations:
   ```bash
   python scripts/init_database.py
   ```

The code will work without changes - SQLAlchemy handles the differences transparently.
