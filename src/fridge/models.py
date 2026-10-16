from datetime import date, datetime, timedelta
from .db import get_connection

VALID_CATEGORIES = [
    'beef', 'fish', 'chicken', 'pork',
    'vegetarian', 'dessert', 'breakfast',
    'sauce', 'pesto', 'tomato_sauce', 'other',
]
VALID_STORAGES = ['freezer', 'fridge']


def add_item(name: str, category: str, storage: str = 'freezer', notes: str = None) -> dict:
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category. Choose from: {', '.join(VALID_CATEGORIES)}")
    if storage not in VALID_STORAGES:
        raise ValueError(f"Invalid storage. Choose from: {', '.join(VALID_STORAGES)}")

    today = date.today().isoformat()
    best_by = (date.today() + timedelta(days=90)).isoformat()

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO items (name, category, storage, quantity, date_added, best_by, notes) VALUES (?, ?, ?, 1, ?, ?, ?)",
        (name.lower(), category, storage, today, best_by, notes)
    )
    conn.commit()
    item = _row_to_dict(conn.execute("SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)).fetchone())
    conn.close()
    return item


def list_items(storage=None, category=None, q=None) -> list:
    conn = get_connection()
    sql = "SELECT * FROM items WHERE 1=1"
    params = []

    if storage:
        sql += " AND storage = ?"
        params.append(storage)
    if category:
        sql += " AND category = ?"
        params.append(category)
    if q:
        sql += " AND name LIKE ?"
        params.append(f"%{q}%")

    sql += " ORDER BY storage, category, name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def search_items(q: str) -> list:
    conn = get_connection()
    sql = "SELECT * FROM items WHERE name LIKE ? OR notes LIKE ? ORDER BY name"
    params = [f"%{q}%", f"%{q}%"]
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def eat_item(item_name: str, servings: int = 1, eaten_date: str = None) -> dict:
    if eaten_date is None:
        eaten_date = date.today().isoformat()

    conn = get_connection()
    item = conn.execute("SELECT * FROM items WHERE name = ?", (item_name.lower(),)).fetchone()
    if not item:
        conn.close()
        raise ValueError(f"Item not found: {item_name}")

    if item['quantity'] < servings:
        conn.close()
        raise ValueError(f"Not enough {item_name}: have {item['quantity']}, want {servings}")

    eaten_dt = datetime.fromisoformat(eaten_date)
    week_number = eaten_dt.isocalendar()[1]

    conn.execute(
        "INSERT INTO dinner_history (item_id, eaten_date, week_number, servings_used) VALUES (?, ?, ?, ?)",
        (item['id'], eaten_date, week_number, servings)
    )
    conn.execute("UPDATE items SET quantity = quantity - ? WHERE id = ?", (servings, item['id']))
    conn.commit()

    updated = _row_to_dict(conn.execute("SELECT * FROM items WHERE id = ?", (item['id'],)).fetchone())
    conn.close()
    return {**updated, "_eaten": True}


def get_weekly_dinners(week_number: int = None) -> list:
    if week_number is None:
        week_number = date.today().isocalendar()[1]

    conn = get_connection()
    sql = """
        SELECT dh.*, i.name, i.category, i.storage
        FROM dinner_history dh
        JOIN items i ON dh.item_id = i.id
        WHERE dh.week_number = ?
        ORDER BY dh.eaten_date DESC
    """
    rows = conn.execute(sql, (week_number,)).fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]


def brainstorm_dinners(storage: str = 'freezer', avoid_week: int = None) -> list:
    """Suggest dinner from available items, avoiding this week's history.
    Flags items past their best-by date and those expiring within 7 days."""
    today = date.today()
    if avoid_week is None:
        avoid_week = today.isocalendar()[1]

    conn = get_connection()

    available = conn.execute(
        "SELECT * FROM items WHERE storage = ? AND quantity > 0 ORDER BY name",
        (storage,)
    ).fetchall()

    eaten = conn.execute(
        "SELECT DISTINCT i.name FROM dinner_history dh JOIN items i ON dh.item_id = i.id WHERE dh.week_number = ?",
        (avoid_week,)
    ).fetchall()
    eaten_names = set(r['name'] for r in eaten)

    suggestions = []
    for item in available:
        if item['name'] in eaten_names:
            continue
        flagged = []
        best_by = item['best_by']
        if best_by:
            best_by_date = date.fromisoformat(best_by)
            if best_by_date < today:
                flagged.append('expired')
            elif (best_by_date - today).days <= 7:
                flagged.append('expiring-soon')
        item_dict = _row_to_dict(item)
        if flagged:
            item_dict['_flagged'] = flagged
        suggestions.append(item_dict)

    conn.close()
    return suggestions


def update_item(item_name: str, **kwargs) -> dict:
    allowed = {'quantity', 'notes', 'best_by'}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return {}

    conn = get_connection()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [item_name.lower()]
    conn.execute(f"UPDATE items SET {set_clause} WHERE name = ?", values)
    conn.commit()
    item = _row_to_dict(conn.execute("SELECT * FROM items WHERE name = ?", (item_name.lower(),)).fetchone())
    conn.close()
    return item


def remove_item(item_name: str) -> bool:
    conn = get_connection()
    cursor = conn.execute("DELETE FROM items WHERE name = ?", (item_name.lower(),))
    conn.commit()
    removed = cursor.rowcount > 0
    conn.close()
    return removed


def _row_to_dict(row):
    if row is None:
        return None
    return dict(row)
