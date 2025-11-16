import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_promotora():
    st.header("👩‍💼 Panel de Promotora")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Multa, Monto, Estado FROM Multa WHERE Estado='Pendiente'")
    multas = cursor.fetchall()

    st.subheader("📌 Multas Pendientes")
    if multas:
        for multa in multas:
            st.write(f"ID: {multa[0]} | Monto: ${multa[1]} | Estado: {multa[2]}")
    else:
        st.info("No hay multas pendientes por el momento.")

