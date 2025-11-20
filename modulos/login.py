import streamlit as st
from modulos.conexion import obtener_conexion
from streamlit_extras.switch_page_button import switch_page
import base64

def login():

    # ----------- ESTILOS CSS -----------
    st.markdown("""
        <style>

        /* Fondo general oscuro */
        body {
            background-color: #0E1117 !important;
        }

        /* Contenedor centrado */
        .login-container {
            max-width: 380px;
            margin: auto;
            margin-top: 60px;
            padding: 30px;
            background: #1A1D23;
            border-radius: 16px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
        }

        /* Texto */
        .login-title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: -5px;
            color: #FFD43B;
        }

        .welcome-text {
            text-align: center;
            color: #ffffff;
            font-size: 17px;
            margin-bottom: 20px;
        }

        /* Input boxes */
        .stTextInput > div > div > input {
            background-color: #2C2F36;
            color: #fff !important;
            border-radius: 10px;
            border: 1px solid #3A3F47;
        }

        /* Botón */
        .stButton button {
            width: 100%;
            background-color: #FFD43B !important;
            color: black !important;
            border-radius: 10px;
            height: 45px;
            font-size: 17px;
            font-weight: 600;
            border: none;
        }

        .stButton button:hover {
            background-color: #ffcc00 !important;
            scale: 1.02;
        }

        /* Labels */
        label {
            font-weight: 600 !important;
            color: #E5E5E5 !important;
        }

        </style>
    """, unsafe_allow_html=True)


    # ----------- ESTRUCTURA DEL LOGIN -----------
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.markdown('<div class="login-title">🔒 SolidARIDAD CVX</div>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-text">Bienvenido a tu sistema Solidaridad CVX</p>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-text" style="font-size:14px; margin-top:-10px;">Ingrese sus credenciales para acceder al sistema</p>', unsafe_allow_html=True)

    usuario = st.text_input("👤 Usuario")
    password = st.text_input("🔑 Contraseña", type="password")

    login_btn = st.button("Iniciar sesión")

    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar container


    # ----------- LÓGICA DEL LOGIN -----------
    if login_btn:
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
                st.session_state["rol"] = datos["Rol"]
                st.session_state["sesion_iniciada"] = True

                st.success("Inicio de sesión exitoso.")
                st.rerun()

            else:
                st.error("❌ Credenciales incorrectas.")

        except Exception as e:
            st.error(f"Error en login: {e}")

