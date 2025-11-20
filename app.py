import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # =========================
    # ESTILOS CORREGIDOS
    # =========================
    st.markdown("""
        <style>

        /* Streamlit usa un div .stApp, NO body */
        .stApp {
            background-color: #0E1117 !important;
        }

        /* Contenedor principal */
        .login-container {
            max-width: 380px;
            margin: auto;
            margin-top: 80px;
            padding: 30px;
            background: #1F232A;
            border-radius: 18px;
            border: solid 1px rgba(255,255,255,0.05);
            box-shadow: 0px 4px 16px rgba(0,0,0,0.45);
        }

        /* Título */
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

        /* Inputs */
        .stTextInput input {
            background-color: #2C3038 !important;
            color: white !important;
            border-radius: 10px !important;
            border: 1px solid #454952 !important;
        }

        /* Botón */
        .stButton button {
            width: 100%;
            background-color: #FFD43B !important;
            color: black !important;
            font-weight: 600;
            border-radius: 10px;
            height: 45px;
            border: none;
        }

        .stButton button:hover {
            background-color: #ffcc00 !important;
        }

        label {
            color: #E5E5E5 !important;
            font-weight: 600 !important;
        }

        </style>
    """, unsafe_allow_html=True)


    # =========================
    # CONTENIDO LOGIN
    # =========================
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    st.markdown('<div class="login-title">🔒 Solidaridad CVX</div>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-text">Bienvenido a tu sistema Solidaridad CVX</p>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-text" style="font-size:14px; margin-top:-10px;">Ingrese sus credenciales para acceder al sistema</p>', unsafe_allow_html=True)

    usuario = st.text_input("👤 Usuario")
    password = st.text_input("🔑 Contraseña", type="password")

    boton = st.button("Iniciar sesión")

    st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # LÓGICA
    # =========================
    if boton:
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

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
