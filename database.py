import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dimsum.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Tabel products (nama, harga, stok, gambar)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            harga INTEGER NOT NULL,
            stok INTEGER NOT NULL DEFAULT 50,
            gambar TEXT
        )
    ''')

    # 2. Tabel customers (wa_number, nama, alamat, state, session_data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wa_number TEXT UNIQUE NOT NULL,
            nama TEXT,
            alamat TEXT,
            state TEXT DEFAULT 'IDLE',
            session_data TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Tabel orders (customer_id, nama_customer, no_wa, alamat, produk, total, status)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            nama_customer TEXT NOT NULL,
            no_wa TEXT NOT NULL,
            alamat TEXT,
            produk TEXT NOT NULL,
            total INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Diproses',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (id)
        )
    ''')

    # Seed data produk jika masih kosong
    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    if count == 0:
        initial_products = [
            ('Dimsum Mentai Original', 25000, 50, 'https://images.unsplash.com/photo-1541696432-82c6da8ce7bf?w=500&auto=format&fit=crop&q=80'),
            ('Dimsum Mentai Spicy', 27000, 50, 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=500&auto=format&fit=crop&q=80'),
            ('Dimsum Mentai Cheese', 30000, 50, 'https://images.unsplash.com/photo-1496116218417-1a781b1c416c?w=500&auto=format&fit=crop&q=80')
        ]
        cursor.executemany(
            'INSERT INTO products (nama, harga, stok, gambar) VALUES (?, ?, ?, ?)',
            initial_products
        )
        print("Data awal produk berhasil ditambahkan ke database.")

    conn.commit()
    conn.close()

# PRODUK HELPERS
def get_all_products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY id ASC').fetchall()
    conn.close()
    return [dict(row) for row in products]

def get_product_by_id(product_id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    conn.close()
    return dict(product) if product else None

def update_product_stock(product_id, qty_sold):
    conn = get_db_connection()
    conn.execute('''
        UPDATE products 
        SET stok = MAX(0, stok - ?) 
        WHERE id = ?
    ''', (qty_sold, product_id))
    conn.commit()
    conn.close()

# CUSTOMER HELPERS
def get_or_create_customer(wa_number, default_name=None):
    clean_wa = str(wa_number).replace('@c.us', '').replace('@s.whatsapp.net', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM customers WHERE wa_number = ?', (clean_wa,))
    row = cursor.fetchone()
    if not row:
        cursor.execute('''
            INSERT INTO customers (wa_number, nama, state, session_data) 
            VALUES (?, ?, 'IDLE', '{}')
        ''', (clean_wa, default_name or 'Pelanggan Dimsum'))
        conn.commit()
        customer_id = cursor.lastrowid
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
    customer = dict(row)
    conn.close()
    return customer

def get_customer_by_wa(wa_number):
    clean_wa = str(wa_number).replace('@c.us', '').replace('@s.whatsapp.net', '').strip()
    conn = get_db_connection()
    row = conn.execute('SELECT * FROM customers WHERE wa_number = ?', (clean_wa,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_customer_session(wa_number, state=None, session_data=None, nama=None, alamat=None):
    clean_wa = str(wa_number).replace('@c.us', '').replace('@s.whatsapp.net', '').strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    values = []
    
    if state is not None:
        updates.append('state = ?')
        values.append(state)
    if session_data is not None:
        updates.append('session_data = ?')
        values.append(json.dumps(session_data) if isinstance(session_data, dict) else session_data)
    if nama is not None:
        updates.append('nama = ?')
        values.append(nama)
    if alamat is not None:
        updates.append('alamat = ?')
        values.append(alamat)
        
    if updates:
        values.append(clean_wa)
        query = f"UPDATE customers SET {', '.join(updates)} WHERE wa_number = ?"
        cursor.execute(query, tuple(values))
        conn.commit()
    conn.close()

# ORDER HELPERS
def create_order(customer_id, nama_customer, no_wa, alamat, produk, total, status='Diproses'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO orders (customer_id, nama_customer, no_wa, alamat, produk, total, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (customer_id, nama_customer, no_wa, alamat, produk, total, status))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id

def get_all_orders():
    conn = get_db_connection()
    orders = conn.execute('SELECT * FROM orders ORDER BY id DESC').fetchall()
    conn.close()
    return [dict(row) for row in orders]

def get_order_by_id(order_id):
    conn = get_db_connection()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    conn.close()
    return dict(order) if order else None

def get_orders_by_customer_wa(wa_number):
    clean_wa = str(wa_number).replace('@c.us', '').replace('@s.whatsapp.net', '').strip()
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT * FROM orders 
        WHERE no_wa LIKE ? 
        ORDER BY id DESC LIMIT 5
    ''', (f'%{clean_wa}%',)).fetchall()
    conn.close()
    return [dict(row) for row in orders]

def update_order_status(order_id, new_status):
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()

def get_admin_stats():
    conn = get_db_connection()
    total_orders = conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
    total_transaksi = conn.execute('SELECT COALESCE(SUM(total), 0) FROM orders WHERE status != "Dibatalkan"').fetchone()[0]
    orders_diproses = conn.execute('SELECT COUNT(*) FROM orders WHERE status = "Diproses"').fetchone()[0]
    orders_selesai = conn.execute('SELECT COUNT(*) FROM orders WHERE status = "Selesai"').fetchone()[0]
    total_customers = conn.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    conn.close()
    return {
        'total_orders': total_orders,
        'total_transaksi': total_transaksi,
        'orders_diproses': orders_diproses,
        'orders_selesai': orders_selesai,
        'total_customers': total_customers
    }

if __name__ == '__main__':
    # Jika tabel lama perlu diperbarui, init_db akan menjamin struktur tabel
    init_db()
    print("Database SQLite dimsum.db siap digunakan.")
