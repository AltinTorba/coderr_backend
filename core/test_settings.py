# core/test_settings.py

# ============================================
# IMPORT SETTINGS FROM MAIN CONFIGURATION
# ============================================
# Import all default settings from the main settings.py file
# This ensures we inherit all existing configuration
# noqa: F401, F403 ignores flake8 warnings for unused imports
from .settings import *  # noqa: F401, F403


# ============================================
# DATABASE CONFIGURATION FOR TESTING
# ============================================
# Override database settings to use SQLite in-memory database
# Benefits:
# - Much faster test execution (no disk I/O)
# - Automatically cleared between tests
# - Isolated from development/production database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # ← In-memory database (extremely fast!)
    }
}


# ============================================
# PASSWORD HASHING FOR TESTING
# ============================================
# Use MD5 hasher instead of default (PBKDF2)
# Benefits:
# - Much faster password hashing during tests
# - Reduced test execution time
# - NOT for production - only for testing!
# Security warning: MD5 is cryptographically weak, but acceptable for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]