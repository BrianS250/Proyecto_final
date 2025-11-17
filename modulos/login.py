import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    st.title("🔐 Inicio de Sesión")
    st.write("Ingrese sus credenciales para acceder al Sistema de Gestión de Grupos.")

    usuario = st.text_input("Usuario")
    contra = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if usuario.strip() == "" or contra.strip() == "":
            st.warning("⚠️ Debe ingresar usuario y contraseña.")
            return

        con = obtener_conexion()
        if not con:
            st.error("❌ Error: No se pudo conectar a la base de datos.")
            return

        try:
            cursor = con.cursor()
            cursor.execute(
                "SELECT Usuario, Contra, Rol FROM Empleado WHERE Usuario = %s",
                (usuario,)
            )
            datos = cursor.fetchone()

            if datos:
                usuario_db, contra_db, rol_db = datos

                if contra == contra_db:
                    # LOGIN ÉXITOSO
                    st.success(f"✨ Bienvenido, **{usuario_db}**")

                    st.session_state["session_iniciada"] = True
                    st.session_state["usuario"] = usuario_db
                    st.session_state["rol"] = rol_db

                    st.rerun()

                else:
                    st.error("❌ Contraseña incorrecta.")

            else:
                st.error("❌ Usuario no encontrado.")

        except Exception as e:
            st.error("⚠️ Error al procesar la solicitud de inicio de sesión.")
            print(e)
