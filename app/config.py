import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/barbershop.db")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Admin Configuration
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "barber")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")  # Will be hashed

# Timezone
TIMEZONE = os.getenv("TIMEZONE", "Europe/Zagreb")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
