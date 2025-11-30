"""
Entrypoint for Gunicorn: creates Flask app and registers routes & middleware.
Procfile uses web.server:app
"""
from flask import Flask
from web.routes import register_routes
from web.middleware import apply_security_headers

def create_app():
    app = Flask(__name__, static_folder="../app/templates", static_url_path="/static")
    apply_security_headers(app)
    register_routes(app)
    return app

app = create_app()
