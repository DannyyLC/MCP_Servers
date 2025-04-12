import sqlite3  

# Conectar a la base de datos (o crearla si no existe)
conn = sqlite3.connect('test.db')  
cursor = conn.cursor()  

# Insertar un dato en la tabla users
cursor.execute("INSERT INTO compras (name, article, amount, price) VALUES ('test', 'CPU', 2, 5000)")  

# Obtener todos los datos de la tabla
cursor.execute("SELECT * FROM compras")  
rows = cursor.fetchall()  # Recuperar todos los registros

# Imprimir los datos
for row in rows:
    print(row)

# Confirmar cambios y cerrar la conexión
conn.commit()  
conn.close()
