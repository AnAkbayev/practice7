"""Centralized PostgreSQL configuration.

Values are loaded from environment variables. Copy .env.example to .env
and set your local credentials, or export the variables in your shell.
"""
import os
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5432"),
    "dbname": os.getenv("PGDATABASE", "phonebook_db"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
}
