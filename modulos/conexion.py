import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="bftcfbzptdyxq4f8afmu-mysql.services.clever-cloud.com",  # Host de Clever Cloud
        user="uXXXXXX",        # Tu usuario real de Clever Cloud
        password="pXXXXXX",    # Tu contraseña real
        database="btfcfbzptdyxq4f8afmu",  # Nombre exacto de la base
        port=3306
    )



