"""
Load critical runtime settings from environment variables.
Do not put secrets here in code; use env vars on Koyeb.
"""
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "please-change-me")
ADMIN_ID = os.getenv("ADMIN_ID", "")
PORT = int(os.getenv("PORT", 8080))

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(ROOT_DIR, "data.db")
CACHE_DIR = os.path.join(ROOT_DIR, "cache")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
