import streamlit as st
from modulos.conexion import obtener_conexion


def login():

    # Si ya está logueado, no pedir login
    if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
        return

    st.title("🔐 Inicio de Sesión")
    st.write("Ingrese sus credenciales para acceder al Sistema de Gestión de Grupos.")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):

        con = obtener_conexion()
        cursor = con.cursor()

        # ---- CONSULTA VALIDADA ----
        cursor.execute("""
            SELECT Usuario, Rol 
            FROM Usuarios
            WHERE Usuario = %s AND Contrasena = %s
        """, (usuario, password))

        datos = cursor.fetchone()

        if datos:
            usuario_db, rol_db = datos

            # ----- GUARDAR SESIÓN -----
            st.session_state["usuario"] = usuario_db
            st.session_state["rol"] = rol_db.lower()
            st.session_state["sesion_iniciada"] = True

            st.success("Inicio de sesión exitoso.")
            st.rerun()  # 🔥 Aquí ya entra a la app

        else:
            st.error("❌ Usuario o contraseña incorrectos.")

