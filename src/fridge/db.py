import sqlite3
from pathlib import Path

DB_DIR = Path.home() / ".local" / "share" / "fridge"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "inventory.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN (
                'beef', 'fish', 'chicken', 'pork',
                'vegetarian', 'dessert', 'breakfast',
                'sauce', 'pesto', 'tomato_sauce', 'other'
            )),
            storage TEXT NOT NULL DEFAULT 'freezer' CHECK(storage IN ('freezer', 'fridge')),
            quantity INTEGER NOT NULL DEFAULT 1,
            date_added TEXT NOT NULL,
            best_by TEXT,
            notes TEXT
        );
        CREATE TABLE IF NOT EXISTS dinner_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL REFERENCES items(id),
            eaten_date TEXT NOT NULL,
            week_number INTEGER NOT NULL,
            servings_used INTEGER NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
        CREATE INDEX IF NOT EXISTS idx_items_storage ON items(storage);
        CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
        CREATE INDEX IF NOT EXISTS idx_dinner_date ON dinner_history(eaten_date);
        CREATE INDEX IF NOT EXISTS idx_dinner_week ON dinner_history(week_number);
    """)
    conn.commit()
    conn.close()
