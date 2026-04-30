import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@db:5432/fixturedb",
)

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

# Optional fallback key for backward compatibility.
LEGACY_API_KEY = os.environ.get("API_KEY", "")

# Optional bootstrap admin account created on startup if missing.
APP_USERNAME = os.environ.get("APP_USERNAME", "")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
