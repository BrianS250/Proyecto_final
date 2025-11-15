import mysql.connector
from mysql.connector import Error

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host='bap6tsdqr200z4fohskz-mysql.services.clever-cloud.com',
            user='uc2dl1ayxtoh4xzo',
            password='tQqq79XsBa5yVMeg7q7r',
            database='bap6tsdqr200z4fohskz',
            port=3306
        )
        if conexion.is_connected():
            print("✅ Conexión establecida")
            return conexion
        else:
            print("❌ Conexión fallida (is_connected = False)")
            return None
    except mysql.connector.Error as e:
        print(f"❌ Error al conectar: {e}")
        return None

