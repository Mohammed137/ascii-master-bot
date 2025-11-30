"""
Message and inline handlers.
Handles:
 - text messages -> ascii
 - photos -> ascii
 - simple commands (/start, /help, /styles)
 - inline queries (basic)
"""
import os
import time
import json
import requests
from ascii_engine import text_to_ascii, image_to_ascii_text, render_text_to_png
from utilities import download_file_from_telegram, record_request, check_rate_limit, safe_send_message, safe_send_photo

TELEGRAM_API_BASE = "https://api.telegram.org"

# Rate limits (tunable)
TEXT_LIMIT_PER_DAY = 200
IMAGE_LIMIT_PER_DAY = 5

def handle_update(update: dict, bot_token: str, db_path: str, admin_id: str):
    # top-level router
    if "message" in update:
        _handle_message(update["message"], bot_token, db_path)
    elif "inline_query" in update:
        _handle_inline(update["inline_query"], bot_token, db_path)
    elif "edited_message" in update:
        # ignore for MVP
        pass
    else:
        # unknown update
        print("Unknown update type:", update.keys())

def _handle_message(msg: dict, bot_token: str, db_path: str):
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    user = msg.get("from", {})
    user_id = user.get("id")
    if "text" in msg:
        text = msg["text"].strip()
        if text.startswith("/"):
            _handle_command(text, chat_id, user_id, bot_token, db_path)
            return
        # normal text -> ascii
        if not check_rate_limit(db_path, user_id, "text", limit=TEXT_LIMIT_PER_DAY):
            safe_send_message(bot_token, chat_id, "⚠️ Text conversion rate limit reached for today.")
            return
        record_request(db_path, user_id, "text")
        ascii_text = text_to_ascii(text)
        # if very long send as PNG
        if len(ascii_text) > 3500:
            out = render_text_to_png(ascii_text)
            safe_send_photo(bot_token, chat_id, out, caption="Here is your ASCII art (image)")
        else:
            safe_send_message(bot_token, chat_id, f"<pre>{ascii_text}</pre>", parse_mode="HTML")
    elif "photo" in msg:
        # image -> ascii
        if not check_rate_limit(db_path, user_id, "image", limit=IMAGE_LIMIT_PER_DAY):
            safe_send_message(bot_token, chat_id, "⚠️ Image conversion rate limit reached for today.")
            return
        record_request(db_path, user_id, "image")
        file_id = msg["photo"][-1]["file_id"]
        try:
            img_bytes = download_file_from_telegram(bot_token, file_id)
            ascii_text = image_to_ascii_text(img_bytes, width=80)
            if len(ascii_text) > 3500:
                out = render_text_to_png(ascii_text)
                safe_send_photo(bot_token, chat_id, out, caption="Your ASCII art (image)")
            else:
                safe_send_message(bot_token, chat_id, f"<pre>{ascii_text}</pre>", parse_mode="HTML")
        except Exception as e:
            print("Image processing error:", e)
            safe_send_message(bot_token, chat_id, "❌ Failed to process the image. Try a smaller image.")

def _handle_command(text, chat_id, user_id, bot_token, db_path):
    cmd = text.split()[0].lower()
    if cmd == "/start":
        msg = (
            "🔥 *AsciiMaster*\n\n"
            "Send text to convert it into ASCII banners.\n"
            "Send a photo and get ASCII art of the image.\n\n"
            "Commands:\n"
            "/help - usage\n"
            "/styles - available text styles\n\n"
            "You can also use inline mode: @AsciiMaster_bot <text>"
        )
        safe_send_message(bot_token, chat_id, msg, parse_mode="Markdown")
    elif cmd == "/help":
        safe_send_message(bot_token, chat_id, "Send text or photo. Use /styles to see ASCII text styles.")
    elif cmd == "/styles":
        sample = text_to_ascii("ASCII")
        # send as text (may be long)
        safe_send_message(bot_token, chat_id, f"<pre>{sample}</pre>", parse_mode="HTML")
    else:
        safe_send_message(bot_token, chat_id, "Unknown command. Use /help.")

def _handle_inline(inline_query: dict, bot_token: str, db_path: str):
    qid = inline_query.get("id")
    qtext = inline_query.get("query", "") or "ascii"
    user = inline_query.get("from", {})
    user_id = user.get("id")
    # rate-limit inline
    if not check_rate_limit(db_path, user_id, "text", limit=TEXT_LIMIT_PER_DAY):
        # return no results
        payload = {
            "inline_query_id": qid,
            "results": [],
            "is_personal": True
        }
        requests.post(f"{TELEGRAM_API_BASE}/bot{bot_token}/answerInlineQuery", json=payload)
        return
    record_request(db_path, user_id, "text")
    ascii_text = text_to_ascii(qtext)
    # craft a single article result
    article = {
        "type": "article",
        "id": "1",
        "title": "ASCII",
        "input_message_content": {"message_text": f"<pre>{ascii_text}</pre>", "parse_mode": "HTML"},
        "description": "Convert text to ASCII using AsciiMaster"
    }
    payload = {"inline_query_id": qid, "results": [article], "is_personal": True}
    requests.post(f"{TELEGRAM_API_BASE}/bot{bot_token}/answerInlineQuery", json=payload)
