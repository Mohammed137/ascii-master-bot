"""
Core bot entrypoint used by the web routes.
This module receives parsed Telegram updates and delegates handling.
"""
import os
import json
from handlers import handle_update

# Exported function for web.routes to call
def process_update(update_json: dict, bot_token: str, db_path: str, admin_id: str):
    """
    Process a Telegram update dictionary.
    Returns a dict with status for easier logging.
    """
    try:
        # delegate to handlers
        handle_update(update_json, bot_token, db_path, admin_id)
        return {"ok": True}
    except Exception as e:
        # bubble up for web layer to log
        return {"ok": False, "error": str(e)}
