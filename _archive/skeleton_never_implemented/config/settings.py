"""
Centralized configuration for the OP Workforce Intelligence & Automation System.

All environment-dependent values (paths, credentials, log level) should be
read from here instead of being hard-coded in individual modules.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# --- Project paths ---
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

OUTPUT_DAILY_DIR = BASE_DIR / "output" / "daily"
OUTPUT_WEEKLY_DIR = BASE_DIR / "output" / "weekly"
OUTPUT_CUSTOM_DIR = BASE_DIR / "output" / "custom"

LOG_DIR = BASE_DIR / "logs"

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# --- Power BI (not used yet) ---
PBI_CLIENT_ID = os.getenv("PBI_CLIENT_ID")
PBI_CLIENT_SECRET = os.getenv("PBI_CLIENT_SECRET")
PBI_TENANT_ID = os.getenv("PBI_TENANT_ID")

# --- Power BI report (Playwright login) ---
PBI_REPORT_URL = os.getenv("PBI_REPORT_URL")
PBI_LOGIN_EMAIL = os.getenv("PBI_LOGIN_EMAIL")
PBI_LOGIN_PASSWORD = os.getenv("PBI_LOGIN_PASSWORD")

# --- Lark (not used yet) ---
LARK_APP_ID = os.getenv("LARK_APP_ID")
LARK_APP_SECRET = os.getenv("LARK_APP_SECRET")
