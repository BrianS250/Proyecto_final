import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="bftcfbzptdyxq4f8afmu-mysql.services.clever-cloud.com",  # tu host en Clever Cloud
        user="uXXXXX",       # tu usuario en Clever Cloud
        password="pXXXXX",   # tu contraseña
        database="btfcfbzptdyxq4f8afmu"
    )


