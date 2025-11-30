"""
Routes:
 - /           -> landing page
 - /webhook/<secret> -> Telegram webhook receiver
 - /cache/... -> serve cached images (if any)
"""
import os
import json
from flask import request, send_from_directory, abort, render_template_string
from app.main import process_update
from config.settings import BOT_TOKEN, WEBHOOK_SECRET, DB_PATH, ADMIN_ID
from app.utilities import init_db

# init DB when module imported
init_db(DB_PATH)

def register_routes(app):
    @app.route("/", methods=["GET"])
    def home():
        # serve simple landing page stored in app/templates/landing.html
        path = os.path.join(os.path.dirname(__file__), "../app/templates/landing.html")
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        return render_template_string(html)

    @app.route(f"/webhook/{WEBHOOK_SECRET}", methods=["POST"])
    def webhook():
        try:
            data = request.get_json(force=True)
        except Exception:
            return {"ok": False, "error": "invalid json"}, 400
        # process update (non-blocking not required for MVP)
        res = process_update(data, BOT_TOKEN, DB_PATH, ADMIN_ID)
        if res.get("ok"):
            return {"ok": True}
        return {"ok": False, "error": res.get("error")}, 500

    @app.route("/cache/<path:filename>")
    def cache_file(filename):
        cache_dir = os.path.join(os.path.dirname(__file__), "../cache")
        file_path = os.path.join(cache_dir, filename)
        if os.path.exists(file_path):
            return send_from_directory(cache_dir, filename)
        abort(404)
