"""
Helpers: Telegram file download, simple sqlite rate-limit, safe send.
"""
import os
import requests
import sqlite3
import time
import hashlib

TELEGRAM_API = "https://api.telegram.org"

# Download file bytes from telegram (getFile -> file path -> download)
def download_file_from_telegram(bot_token: str, file_id: str) -> bytes:
    r = requests.get(f"{TELEGRAM_API}/bot{bot_token}/getFile", params={"file_id": file_id}, timeout=15)
    j = r.json()
    if not j.get("ok"):
        raise RuntimeError("Failed to get file info")
    path = j["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{path}"
    data = requests.get(file_url, timeout=30).content
    return data

# DB utilities for rate-limits and request logging
def _get_conn(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=10)
    return conn

def init_db(db_path):
    conn = _get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        kind TEXT,
        ts INTEGER
    )""")
    conn.commit()
    conn.close()

def record_request(db_path, user_id, kind):
    conn = _get_conn(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO requests (user_id, kind, ts) VALUES (?, ?, ?)", (user_id, kind, int(time.time())))
    conn.commit()
    conn.close()

def check_rate_limit(db_path, user_id, kind, limit=100, period_seconds=86400):
    conn = _get_conn(db_path)
    cur = conn.cursor()
    cutoff = int(time.time()) - period_seconds
    cur.execute("SELECT COUNT(*) FROM requests WHERE user_id=? AND kind=? AND ts>?", (user_id, kind, cutoff))
    count = cur.fetchone()[0]
    conn.close()
    return count < limit

# Safe send helpers
def safe_send_message(bot_token: str, chat_id: int, text: str, parse_mode: str = None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    r = requests.post(f"{TELEGRAM_API}/bot{bot_token}/sendMessage", json=payload, timeout=15)
    if r.status_code != 200:
        print("sendMessage failed:", r.status_code, r.text)
    return r

def safe_send_photo(bot_token: str, chat_id: int, photo_path: str, caption: str = None):
    url = f"{TELEGRAM_API}/bot{bot_token}/sendPhoto"
    with open(photo_path, "rb") as f:
        files = {"photo": f}
        data = {"chat_id": str(chat_id)}
        if caption:
            data["caption"] = caption
        r = requests.post(url, files=files, data=data, timeout=30)
    if r.status_code != 200:
        print("sendPhoto failed:", r.status_code, r.text)
    return r
