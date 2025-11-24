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
            # Autenticar por usuario/contraseña y obtener el rol REAL
            # desde la tabla Roles (mapear Empleado.Rol -> Roles.Tipo_de_rol)
            cursor.execute("""
                SELECT e.Usuario, r.Tipo_de_rol
                FROM Empleado e
                JOIN Roles r
                    ON r.Tipo_de_rol = e.Rol
                WHERE e.Usuario = %s
                  AND e.Contra = %s
            """, (usuario, password))

            datos = cursor.fetchone()

            if datos:
                st.session_state["usuario"] = datos["Usuario"]
                st.session_state["rol"] = datos["Tipo_de_rol"]   # ← ahora viene de Roles
                st.session_state["sesion_iniciada"] = True

                st.success("Inicio de sesión exitoso.")
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas o rol no configurado.")

        except Exception as e:
            st.error(f"Error en login: {e}")

        finally:
            cursor.close()
            con.close()

            
