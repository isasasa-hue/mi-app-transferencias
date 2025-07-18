import sqlite3

def crear_tabla():
    conn = sqlite3.connect("transferencias.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transferencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            monto REAL,
            cliente TEXT,
            fecha_pedido TEXT,
            fecha_transferencia TEXT,
            fecha_retiro TEXT,
            factura TEXT
        )
    ''')
    conn.commit()
    conn.close()