import click
from datetime import date
from .db import init_db
from . import models


@click.group()
def main():
    """Freezer & Fridge Inventory Tracker"""
    init_db()


@main.command()
@click.argument('name')
@click.option('--category', '-c', required=True, help=f"Category: {', '.join(models.VALID_CATEGORIES)}")
@click.option('--storage', '-s', default='freezer', type=click.Choice(['freezer', 'fridge']), help="Where is it stored?")
@click.option('--notes', '-n', default=None, help="Optional notes")
def add(name, category, storage, notes):
    """Add an item to inventory."""
    try:
        item = models.add_item(name, category, storage, notes)
        click.echo(f"Added: {item['name']} ({item['category']}) in {item['storage']}, qty={item['quantity']}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@main.command()
@click.option('--storage', '-s', type=click.Choice(['freezer', 'fridge']), default=None, help="Filter by storage")
@click.option('--category', '-c', default=None, help="Filter by category")
@click.option('--q', default=None, help="Search by name")
def list(storage, category, q):
    """List inventory items."""
    items = models.list_items(storage=storage, category=category, q=q)
    if not items:
        click.echo("No items found.")
        return

    click.echo(f"\n{'Name':<30} {'Category':<14} {'Storage':<10} {'Qty':<5} {'Best By':<12}")
    click.echo("-" * 75)
    for item in items:
        click.echo(f"{item['name']:<30} {item['category']:<14} {item['storage']:<10} {item['quantity']:<5} {item['best_by'] or 'N/A':<12}")

    click.echo(f"\nTotal: {len(items)} items")


@main.command()
@click.argument('name')
@click.option('--servings', '-n', default=1, type=int, help="Number of servings to deduct")
@click.option('--date', '-d', default=None, help="Date eaten (YYYY-MM-DD, default today)")
def eat(name, servings, date):
    """Record eating a dinner. Deducts from inventory."""
    try:
        item = models.eat_item(name, servings, date)
        click.echo(f"Recorded: {item['name']} x{servings} eaten on {date or 'today'}. Remaining: {item['quantity']}")
    except ValueError as e:
        click.echo(f"Error: {e}")


@main.command('brainstorm')
@click.option('--storage', '-s', default='freezer', help="Search which storage?")
def brainstorm(storage):
    """Suggest dinner from available items (avoids this week's history, flags expired)."""
    suggestions = models.brainstorm_dinners(storage)
    if not suggestions:
        click.echo(f"No {storage} items available for dinner brainstorming.")
        return

    expired = [s for s in suggestions if 'expired' in s.get('_flagged', [])]
    expiring = [s for s in suggestions if 'expiring-soon' in s.get('_flagged', [])]
    safe = [s for s in suggestions if not s.get('_flagged')]

    click.echo(f"\n🍽️ Dinner ideas from your {storage}:")

    if expired:
        click.echo(f"\n⚠️  EXPIRED (best-by passed):")
        for item in expired:
            click.echo(f"  🔴 {item['name']} ({item['category']}) — {item['quantity']} left")

    if expiring:
        click.echo(f"\n⏰  EXPIRING SOON (within 7 days):")
        for item in expiring:
            click.echo(f"  🟡 {item['name']} ({item['category']}) — {item['quantity']} left (best by: {item['best_by']})")

    if safe:
        click.echo(f"\n✅  GOOD TO EAT:")
        for item in safe:
            click.echo(f"  🟢 {item['name']} ({item['category']}) — {item['quantity']} left")

    click.echo(f"\n({len(safe)} safe options. Already eaten this week excluded. {len(expired)} expired, {len(expiring)} expiring soon.)")


@main.command()
@click.option('--week', '-w', default=None, type=int, help="Week number (default: current)")
def history(week):
    """Show dinners eaten in a given week."""
    if week is None:
        week = date.today().isocalendar()[1]

    dinners = models.get_weekly_dinners(week)
    if not dinners:
        click.echo(f"No dinners recorded for week {week}.")
        return

    click.echo(f"\n📋 Week {week} dinner history:")
    for d in dinners:
        click.echo(f"  {d['eaten_date']}: {d['name']} ({d['category']}) x{d['servings_used']}")


@main.command()
@click.argument('query')
def search(query):
    """Search items by name."""
    items = models.search_items(query)
    if not items:
        click.echo(f"No items matching '{query}'.")
        return

    click.echo(f"\nResults for '{query}':")
    for item in items:
        click.echo(f"  {item['name']} ({item['category']}) — {item['storage']}, qty={item['quantity']}")


@main.command()
@click.argument('name')
@click.option('--quantity', '-q', default=None, type=int, help="New quantity")
@click.option('--notes', '-n', default=None, help="New notes")
@click.option('--best-by', default=None, help="New best-by date (YYYY-MM-DD)")
def update(name, quantity, notes, best_by):
    """Update an item's details."""
    updates = {}
    if quantity is not None:
        updates['quantity'] = quantity
    if notes is not None:
        updates['notes'] = notes
    if best_by is not None:
        updates['best_by'] = best_by

    if not updates:
        click.echo("Nothing to update. Specify --quantity, --notes, or --best-by.")
        return

    item = models.update_item(name, **updates)
    if not item:
        click.echo(f"Item not found: {name}")
        return
    click.echo(f"Updated: {item['name']}")


@main.command()
@click.argument('name')
def remove(name):
    """Remove an item from inventory."""
    if models.remove_item(name):
        click.echo(f"Removed: {name}")
    else:
        click.echo(f"Item not found: {name}")


if __name__ == '__main__':
    main()
