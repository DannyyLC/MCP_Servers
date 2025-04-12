import sqlite3

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

# crear tabla
cursor.execute('''
CREATE TABLE IF NOT EXISTS compras(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    article TEXT,
    amount INTEGER,
    price FLOAT,
    total FLOAT GENERATED ALWAYS AS (amount * price) STORED
)
''')

conn.commit()
conn.close()