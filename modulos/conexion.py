import mysql.connector
import streamlit as st

def obtener_conexion():
    try:
        return mysql.connector.connect(
            host="btcfcbzptdyxq4f8afmu-mysql.services.clever-cloud.com",
            port=3306,
            user="unruvixx62rfxqfi5",
            password="thsm5lvj3szedOcs1mIzL",
            database="btcfcbzptdyxq4f8afmu",
            ssl_ca=None,              # <--- si tu BD NO requiere SSL
            ssl_disabled=True         # <--- fuerza conexión sin SSL
        )
    except Exception as e:
        st.error(f"❌ Error al conectar con la base de datos: {e}")
        return None



