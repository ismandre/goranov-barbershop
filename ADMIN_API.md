# Admin API Documentation

JWT-based authentication API for managing appointments and availability.

## Quick Start

### 1. Start Server

```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

### 2. Interactive API Docs

Open your browser to:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Create Admin User

```bash
python scripts/create_admin.py --username barber --password barber123
```

## Authentication Flow

### Step 1: Login

**POST** `/admin/auth/login`

```bash
curl -X POST http://localhost:8000/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "barber",
    "password": "barber123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 86400,
  "admin_id": 1,
  "username": "barber"
}
```

### Step 2: Use Token

Include in all subsequent requests:

```bash
curl http://localhost:8000/admin/stats \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

## API Endpoints

### Authentication

#### Login
```
POST /admin/auth/login
```
Get JWT access token.

#### Get Current Admin
```
GET /admin/auth/me
```
Get current authenticated admin info. Requires auth.

#### Verify Token
```
POST /admin/auth/verify
```
Check if token is valid. Requires auth.

---

### Appointments

#### Get All Appointments
```
GET /admin/appointments?date=2024-12-05&status=pending
```

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD)
- `status` (optional): pending | confirmed | completed | cancelled | no_show

**Example:**
```bash
curl "http://localhost:8000/admin/appointments?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "customer_phone": "+385991234567",
    "customer_name": null,
    "start_time": "2024-12-05T10:00:00",
    "end_time": "2024-12-05T10:30:00",
    "status": "confirmed",
    "booked_at": "2024-12-04T15:30:00",
    "notes": null
  }
]
```

#### Update Appointment Status
```
PATCH /admin/appointments/{appointment_id}
```

**Body:**
```json
{
  "status": "completed"
}
```

**Valid Statuses:**
- `pending` - Awaiting confirmation
- `confirmed` - Confirmed appointment
- `completed` - Customer showed up, service completed
- `cancelled` - Cancelled by customer or admin
- `no_show` - Customer didn't show up

**Example:**
```bash
curl -X PATCH http://localhost:8000/admin/appointments/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

---

### Time Slots

#### Get All Slots
```
GET /admin/slots?date=2024-12-05&available_only=true
```

**Query Parameters:**
- `date` (optional): Filter by date (YYYY-MM-DD)
- `available_only` (optional): Show only unbooked slots (true/false)

**Example:**
```bash
curl "http://localhost:8000/admin/slots?available_only=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "start_time": "2024-12-05T10:00:00",
    "end_time": "2024-12-05T10:30:00",
    "is_booked": false
  }
]
```

#### Create Slot
```
POST /admin/slots
```

**Body:**
```json
{
  "start_time": "2024-12-05T14:00:00",
  "end_time": "2024-12-05T14:30:00"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/admin/slots \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2024-12-05T14:00:00",
    "end_time": "2024-12-05T14:30:00"
  }'
```

**Response:**
```json
{
  "success": true,
  "id": 25,
  "start_time": "2024-12-05T14:00:00",
  "end_time": "2024-12-05T14:30:00"
}
```

#### Delete Slot
```
DELETE /admin/slots/{slot_id}
```

Cannot delete booked slots.

**Example:**
```bash
curl -X DELETE http://localhost:8000/admin/slots/25 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Dashboard Statistics

#### Get Stats
```
GET /admin/stats
```

**Example:**
```bash
curl http://localhost:8000/admin/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "today_appointments": 5,
  "pending_confirmations": 2,
  "available_slots": 8,
  "total_customers": 120
}
```

---

## Testing

### Automated Tests

```bash
# Make sure server is running
uvicorn app.main:app --reload

# Run tests
python tests/test_admin_api.py
```

### Manual Testing with curl

```bash
# 1. Login and save token
TOKEN=$(curl -s -X POST http://localhost:8000/admin/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"barber","password":"barber123"}' \
  | jq -r '.access_token')

# 2. Get stats
curl http://localhost:8000/admin/stats \
  -H "Authorization: Bearer $TOKEN"

# 3. Get appointments
curl http://localhost:8000/admin/appointments \
  -H "Authorization: Bearer $TOKEN"

# 4. Get available slots
curl "http://localhost:8000/admin/slots?available_only=true" \
  -H "Authorization: Bearer $TOKEN"

# 5. Create slot
curl -X POST http://localhost:8000/admin/slots \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2024-12-10T15:00:00",
    "end_time": "2024-12-10T15:30:00"
  }'
```

### Using Swagger UI

1. Start server: `uvicorn app.main:app --reload`
2. Open http://localhost:8000/docs
3. Click "Authorize" button (top right)
4. Login first: POST `/admin/auth/login`
5. Copy the `access_token` from response
6. Click "Authorize" and paste token (with "Bearer " prefix)
7. Now you can test all endpoints interactively!

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

**Causes:**
- No token provided
- Invalid token
- Expired token
- Wrong credentials

### 404 Not Found
```json
{
  "detail": "Appointment not found"
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD"
}
```

---

## Security Notes

1. **Token Expiration**: Tokens expire after 24 hours (configurable in `config.py`)
2. **HTTPS Only in Production**: Always use HTTPS in production
3. **CORS**: Currently set to allow all origins (`*`) - restrict in production
4. **Password Hashing**: Uses bcrypt for secure password storage
5. **Token Storage**: Never commit tokens to git or logs

---

## Configuration

Environment variables (`.env`):

```env
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

class AdminClient:
    def __init__(self, username: str, password: str):
        self.base_url = BASE_URL
        self.token = None
        self.login(username, password)

    def login(self, username: str, password: str):
        response = requests.post(
            f"{self.base_url}/admin/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        self.token = response.json()["access_token"]

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def get_stats(self):
        response = requests.get(
            f"{self.base_url}/admin/stats",
            headers=self.headers
        )
        return response.json()

    def get_appointments(self, date=None, status=None):
        params = {}
        if date:
            params["date"] = date
        if status:
            params["status"] = status

        response = requests.get(
            f"{self.base_url}/admin/appointments",
            headers=self.headers,
            params=params
        )
        return response.json()

    def create_slot(self, start_time: str, end_time: str):
        response = requests.post(
            f"{self.base_url}/admin/slots",
            headers=self.headers,
            json={"start_time": start_time, "end_time": end_time}
        )
        return response.json()

# Usage
client = AdminClient("barber", "barber123")
stats = client.get_stats()
print(f"Today's appointments: {stats['today_appointments']}")

appointments = client.get_appointments(status="pending")
print(f"Pending: {len(appointments)}")
```

---

## Next Steps

1. **Build Admin Dashboard UI** - Frontend to consume this API
2. **Add More Endpoints** - Bulk operations, reports, customer management
3. **Implement Refresh Tokens** - Long-lived sessions
4. **Add Rate Limiting** - Prevent abuse
5. **Add Logging** - Audit trail for admin actions

See `DESIGN.md` for Phase 3 (Admin Dashboard UI) specifications.
