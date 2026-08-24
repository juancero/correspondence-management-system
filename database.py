import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_NAME = "data_demo.db"

DB_PATH = BASE_DIR / DB_NAME

SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_db_name():
    return DB_NAME


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo schema.sql en {SCHEMA_PATH}")

    with get_connection() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    print("Base de datos inicializada correctamente.")


if __name__ == "__main__":
    init_db()
