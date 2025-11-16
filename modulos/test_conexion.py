from modulos.conexion import obtener_conexion

try:
    con = obtener_conexion()
    print("✅ Conexión exitosa a la base de datos")
    con.close()
except Exception as e:
    print("❌ Error:", e)
