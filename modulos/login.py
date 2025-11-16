import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.title("🔐 Iniciar sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute(
            "SELECT Usuario, Contra, Rol FROM Empleado WHERE Usuario=%s AND Contra=%s",
            (usuario, contra)
        )
        fila = cursor.fetchone()

        if fila:
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = fila[2]
            st.success(f"✅ Bienvenido, {fila[0]} ({fila[2]})")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
