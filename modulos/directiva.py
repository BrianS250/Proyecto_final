import streamlit as st
from modulos.Configuracion.conexion import obtener_conexion

def interfaz_directiva():
    st.header("🏛️ Panel de Directiva")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM Multa")
    multas = cursor.fetchall()

    st.subheader("📋 Registro de Multas")
    if multas:
        for multa in multas:
            st.write(f"ID: {multa[0]} | Monto: ${multa[2]} | Estado: {multa[4]}")
    else:
        st.info("No hay multas registradas.")
