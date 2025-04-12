import sqlite3  

# Conectar a la base de datos
conn = sqlite3.connect('test.db')  
cursor = conn.cursor()  

# Verificar si la tabla 'compras' existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='compras'")
if not cursor.fetchone():
    print("La tabla 'compras' no existe.")
else:
    # Insertar un dato en la tabla compras
    cursor.execute("INSERT INTO compras (name, article, amount, price) VALUES ('test', 'CPU', 2, 5000)")  
    conn.commit()  # Confirmar la inserción

    # Obtener todos los datos de la tabla
    cursor.execute("SELECT * FROM compras")  
    rows = cursor.fetchall()  

    # Imprimir los datos
    for row in rows:
        print(row)

# Obtener nombres de las tablas correctamente
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

db_structure = {}

for table in tables:
    table_name = table[0]
    
    # Obtener las columnas de cada tabla
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    db_structure[table_name] = [column[1] for column in columns]

print(db_structure)

conn.close()  

