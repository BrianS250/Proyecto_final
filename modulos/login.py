import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    st.title("Inicio de sesión")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Usuario, Rol 
            FROM Usuarios 
            WHERE Usuario = %s AND Contrasena = %s
        """, (usuario, password))
        
        fila = cursor.fetchone()

        if fila:
            usuario_db, rol_db = fila

            # NORMALIZAMOS EL ROL A MINÚSCULAS
            rol_db = rol_db.strip().lower()

            # Guardamos sesión
            st.session_state["usuario"] = usuario_db
            st.session_state["rol"] = rol_db  # <--- CRÍTICO
            st.session_state["sesion_iniciada"] = True

            st.success("Ingreso exitoso 🎉")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
