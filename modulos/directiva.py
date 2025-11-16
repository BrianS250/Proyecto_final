import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_directiva():
    st.header("🏛️ Panel de Directiva del Grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Multa, Fecha_aplicacion, Monto, Estado FROM Multa")
    datos = cursor.fetchall()

    st.subheader("📋 Listado de Multas Registradas")
    if datos:
        for multa in datos:
            st.write(f"🆔 {multa[0]} | 💰 ${multa[2]} | 📅 {multa[1]} | 🏷️ {multa[3]}")
    else:
        st.info("No hay multas registradas en el sistema.")
