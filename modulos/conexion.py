import mysql.connector
import streamlit as st

def obtener_conexion():
    try:
        return mysql.connector.connect(
            host="btcfcbzptdyxq4f8afmu-mysql.services.clever-cloud.com",
            user="unruixx62rfqfqi5",
            password="tHsn5wIjxSzedGOsZmtL",
            database="btcfcbzptdyxq4f8afmu",
            port=3306
        )

    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
        return None





