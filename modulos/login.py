import streamlit as st
from modulos.conexion import obtener_conexion
from modulos.directiva import interfaz_directiva


def login():

    st.title("🔐 Inicio de Sesión")
    st.write("Ingrese sus credenciales para acceder al sistema.")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):

        con = obtener_conexion()
        cursor = con.cursor()

        try:
            cursor.execute("""
                SELECT Usuario, Rol 
                FROM Empleado 
                WHERE Usuario = %s AND Contra = %s
            """, (usuario, password))

            datos = cursor.fetchone()

            if datos:
                # Guardamos usuario y rol en sesión
                st.session_state["usuario"] = datos[0]
                st.session_state["rol"] = datos[1]
                st.session_state["sesion_iniciada"] = True
                st.success("Inicio de sesión exitoso.")
                st.rerun()

            else:
                st.error("❌ Credenciales incorrectas.")

        except Exception as e:
            st.error(f"Error en login: {e}")
