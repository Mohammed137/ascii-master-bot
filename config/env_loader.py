"""
Optional helper for local development to load .env.
"""
from dotenv import load_dotenv
import os

def load_local_env(path=".env"):
    if os.path.exists(path):
        load_dotenv(path)
