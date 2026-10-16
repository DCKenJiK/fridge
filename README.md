# 🧊 Fridge Inventory

Freezer & fridge inventory tracker with dinner brainstorming. Track your frozen dinners, manage fridge items, and get dinner suggestions — all through a CLI or web UI.

## Features

- **CLI tool** — access via terminal or through Hermes AI
- **Web UI** — browse, search, filter, and manage inventory at `localhost:8787`
- **Dinner brainstorming** — suggestions exclude what you've eaten this week
- **Expiry alerts** — flags items past their best-by date and those expiring soon
- **Weekly history** — track what you've eaten to avoid repeats
- **Categories** — beef, fish, chicken, pork, vegetarian, breakfast, dessert, sauce, pesto, tomato_sauce, other

## Install

```bash
cd /Users/kenkirkpatrick/projects/fridge
pip install -e .
```

## Usage

### CLI

```bash
# Add an item
fridge add "beef stew" --category beef --storage freezer --notes "Makes 3 portions"

# List all freezer items
fridge list --storage freezer

# Brainstorm dinner ideas (flags expired/expiring items)
fridge brainstorm

# Record eating a dinner
fridge eat "beef stew" --servings 1

# View weekly dinner history
fridge history

# Search
fridge search "chicken"
```

### Web App

```bash
python -m fridge.main
```

Then open http://localhost:8787 in your browser.

### Seed Data

```bash
python scripts/seed.py
```

## Architecture

- **Database:** SQLite (`~/.local/share/fridge/inventory.db`)
- **Storage:** Items + dinner_history tables
- **Default best-by:** 90 days from date added
- **Expiry flags:** expired (past best-by) and expiring-soon (within 7 days)

## Data Model

### items
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | |
| name | TEXT NOT NULL | item name |
| category | TEXT | beef, fish, chicken, pork, vegetarian, breakfast, dessert, sauce, pesto, tomato_sauce, other |
| storage | TEXT | freezer or fridge |
| quantity | INTEGER | number of portions |
| date_added | TEXT | ISO date |
| best_by | TEXT | ISO date (default +90 days) |
| notes | TEXT | optional freeform |

### dinner_history
| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PRIMARY KEY | |
| item_id | INTEGER FK → items.id | |
| eaten_date | TEXT | ISO date |
| week_number | INTEGER | ISO week (for dedup) |
| servings_used | INTEGER | deducted from item quantity |
