import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",           # tu usuario MySQL
        password="",           # si tienes contraseña, ponla aquí
        database="btcfcbzptdyxq4f8afmu"  # nombre exacto de tu BD
    )
