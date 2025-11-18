import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.header("🔐 Inicio de Sesión")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        if not con:
            st.error("❌ Error: No se pudo conectar a la base de datos.")
            return

        cursor = con.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Empleado WHERE Usuario = %s AND Contra = %s",
            (usuario, contra)
        )
        fila = cursor.fetchone()

        if fila:
            st.success("✅ Inicio de sesión exitoso.")
            st.session_state["sesion_iniciada"] = True
            st.session_state["rol"] = fila["Rol"]     # ← IMPORTANTE
            st.session_state["usuario"] = fila["Usuario"]
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")
