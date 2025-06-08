# settings.py

# CORS configuration
CORS_ORIGINS = ["*"]

# Flask configuration
SECRET_KEY = "your_secret_key"
BUNDLE_ERRORS = True

# File upload path
STATIC_DIRECTORY = "static"

# Firebase configuration (no env vars)
USE_FIRESTORE_EMULATOR = True  # Set this to False for production
FIRESTORE_EMULATOR_HOST = "localhost:8080"