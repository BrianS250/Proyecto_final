import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.title("🔐 Inicio de Sesión")
    st.write("Ingrese sus credenciales para acceder al sistema.")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT Usuario, Rol
                FROM Empleado
                WHERE Usuario = %s AND Contra = %s
            """, (usuario, password))

            datos = cursor.fetchone()

            if datos:

                st.session_state["usuario"] = datos["Usuario"]
                st.session_state["rol"] = datos["Rol"]  # ← tal cual viene de BD
                st.session_state["sesion_iniciada"] = True

                st.success("Inicio de sesión exitoso.")
                st.rerun()

            else:
                st.error("❌ Credenciales incorrectas.")

        except Exception as e:
            st.error(f"Error en login: {e}")

