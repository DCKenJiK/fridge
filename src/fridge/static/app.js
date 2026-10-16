const API = '/api';
let currentStorage = 'freezer';
let currentCategory = '';
let searchQuery = '';

async function loadItems() {
    let url = `${API}/items?storage=${currentStorage}`;
    if (currentCategory) url += `&category=${currentCategory}`;
    if (searchQuery) url += `&q=${searchQuery}`;

    const res = await fetch(url);
    const items = await res.json();
    renderItems(items);
}

function renderItems(items) {
    const grid = document.getElementById('itemGrid');
    const empty = document.getElementById('emptyState');

    if (items.length === 0) {
        grid.innerHTML = '';
        empty.style.display = 'block';
        return;
    }

    empty.style.display = 'none';
    grid.innerHTML = items.map(item => {
        const flags = item._flagged || [];
        const flagBadges = flags.map(f => {
            if (f === 'expired') return '<span class="flag-badge flag-expired">⚠️ EXPIRED</span>';
            if (f === 'expiring-soon') return '<span class="flag-badge flag-expiring-soon">⏰ Exp soon</span>';
            return '';
        }).join(' ');
        const borderColor = flags.includes('expired') ? 'border-color: #e74c3c; border-width: 2px;' : '';
        return `
        <div class="item-card" style="${borderColor}">
            <div class="name">${item.name} ${flagBadges}</div>
            <div class="meta">
                <span class="category-tag cat-${item.category}">${item.category}</span>
                <span class="badge">${item.quantity} left</span>
            </div>
            ${item.notes ? `<div style="font-size:0.8em;color:#888;margin-top:4px;">${item.notes}</div>` : ''}
            <div style="font-size:0.75em;color:#aaa;margin-top:6px;">Best by: ${item.best_by || 'N/A'}</div>
            <div class="actions">
                <button class="eat-btn" onclick="eatItem(${item.id}, '${item.name}')">🍽️ Eat</button>
                <button class="del-btn" onclick="deleteItem(${item.id}, '${item.name}')">🗑️</button>
            </div>
        </div>
    `;
    }).join('');
}

async function eatItem(id, name) {
    const servings = prompt(`How many servings of ${name}?`, "1");
    if (!servings) return;

    await fetch(`${API}/dinners`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ item_name: name, servings: parseInt(servings) })
    });

    await loadItems();
    await loadHistory();
}

async function deleteItem(id, name) {
    if (!confirm(`Remove "${name}" from inventory?`)) return;
    await fetch(`${API}/items/${id}`, { method: 'DELETE' });
    await loadItems();
}

async function addItem() {
    const name = document.getElementById('itemName').value.trim();
    const category = document.getElementById('itemCategory').value;
    const storage = document.getElementById('itemStorage').value;
    const notes = document.getElementById('itemNotes').value.trim();

    if (!name) { alert('Name is required'); return; }

    await fetch(`${API}/items`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ name, category, storage, notes })
    });

    document.getElementById('addModal').classList.remove('open');
    document.getElementById('itemName').value = '';
    document.getElementById('itemNotes').value = '';
    await loadItems();
}

async function loadHistory() {
    const res = await fetch(`${API}/dinners`);
    const dinners = await res.json();
    const list = document.getElementById('historyList');

    if (dinners.length === 0) {
        list.innerHTML = '<p style="color:#999;font-size:0.9em;">No dinners this week yet.</p>';
        return;
    }

    list.innerHTML = dinners.map(d => `
        <div class="history-item">
            <strong>${d.name}</strong> (${d.category}) — ${d.eaten_date}<br>
            <span style="font-size:0.85em;color:#888;">x${d.servings_used} serving${d.servings_used > 1 ? 's' : ''}</span>
        </div>
    `).join('');
}

document.querySelectorAll('.storage-toggle button').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.storage-toggle button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentStorage = btn.dataset.storage;
        currentCategory = '';
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('.filter-btn[data-category=""]').classList.add('active');
        loadItems();
    });
});

document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentCategory = btn.dataset.category;
        loadItems();
    });
});

document.getElementById('searchInput').addEventListener('input', (e) => {
    searchQuery = e.target.value;
    loadItems();
});

document.getElementById('addBtn').addEventListener('click', () => {
    document.getElementById('addModal').classList.add('open');
});

document.getElementById('cancelBtn').addEventListener('click', () => {
    document.getElementById('addModal').classList.remove('open');
});

document.getElementById('submitBtn').addEventListener('click', addItem);

document.getElementById('historyToggle').addEventListener('click', () => {
    document.getElementById('historyPanel').classList.toggle('open');
    loadHistory();
});

loadItems();
