from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from .db import init_db
from . import models

app = FastAPI(title="Fridge Inventory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ItemCreate(BaseModel):
    name: str
    category: str
    storage: str = "freezer"
    notes: Optional[str] = None


class ItemUpdate(BaseModel):
    quantity: Optional[int] = None
    notes: Optional[str] = None
    best_by: Optional[str] = None


class DinnerRecord(BaseModel):
    item_name: str
    servings: int = 1
    eaten_date: Optional[str] = None


@app.on_event("startup")
def startup():
    init_db()


# ── Items ──

@app.get("/api/items")
def get_items(storage: Optional[str] = None, category: Optional[str] = None, q: Optional[str] = None):
    return models.list_items(storage=storage, category=category, q=q)


@app.get("/api/items/{item_id}")
def get_item(item_id: int):
    conn = models.get_connection()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    if not item:
        raise HTTPException(404, "Item not found")
    return dict(item)


@app.post("/api/items", status_code=201)
def create_item(item: ItemCreate):
    try:
        return models.add_item(item.name, item.category, item.storage, item.notes)
    except ValueError as e:
        raise HTTPException(400, str(e))


@app.put("/api/items/{item_id}")
def update_item(item_id: int, updates: ItemUpdate):
    conn = models.get_connection()
    db_item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    if not db_item:
        conn.close()
        raise HTTPException(404, "Item not found")

    update_data = updates.model_dump(exclude_none=True)
    if not update_data:
        return dict(db_item)

    set_clause = ", ".join(f"{k} = ?" for k in update_data)
    values = list(update_data.values()) + [item_id]
    conn.execute(f"UPDATE items SET {set_clause} WHERE id = ?", values)
    conn.commit()
    updated = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(updated)


@app.delete("/api/items/{item_id}", status_code=204)
def delete_item(item_id: int):
    conn = models.get_connection()
    cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(404, "Item not found")
    conn.close()


# ── Dinners ──

@app.get("/api/dinners")
def get_dinners(week: Optional[int] = None):
    return models.get_weekly_dinners(week)


@app.post("/api/dinners", status_code=201)
def record_dinner(record: DinnerRecord):
    try:
        result = models.eat_item(record.item_name, record.servings, record.eaten_date)
        return result
    except ValueError as e:
        raise HTTPException(400, str(e))


# ── Brainstorm ──

@app.get("/api/brainstorm")
def brainstorm(storage: str = "freezer"):
    return models.brainstorm_dinners(storage)


# ── Search ──

@app.get("/api/search")
def search(q: str = Query(..., min_length=1)):
    return models.search_items(q)


# ── Static Files ──

STATIC_DIR = Path(__file__).parent / "static"

@app.get("/")
def serve_index():
    return FileResponse(STATIC_DIR / "index.html")

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
