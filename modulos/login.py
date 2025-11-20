import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # CONFIGURACIÓN Y ESTILOS --------------------------------------------
    st.markdown("""
        <style>

            /* Fondo oscuro general */
            body {
                background-color: #0e1117 !important;
            }

            /* Contenedor principal centrado */
            .login-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin-top: 40px;
            }

            /* Caja del formulario */
            .login-box {
                background-color: #161a23;
                padding: 30px;
                width: 90%;
                max-width: 380px;
                border-radius: 18px;
                box-shadow: 0px 4px 20px rgba(0,0,0,0.6);
                margin-top: 20px;
            }

            /* Logo centrado */
            .logo-container img {
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 140px;
                filter: brightness(0.90);
            }

            /* Título */
            h2 {
                text-align: center;
                color: #e3e6ed !important;
                font-weight: 700;
            }

            /* Inputs */
            .stTextInput > div > div > input {
                background-color: #1f2430 !important;
                color: #ffffff !important;
                border: 1px solid #444a55 !important;
                border-radius: 8px;
                padding: 10px;
            }

            /* Quitar sombra superior extra */
            .st-emotion-cache-1dp5vir {
                display: none;
            }

            /* Botón verde */
            .stButton > button {
                width: 100%;
                background-color: #2e7d32 !important;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                padding: 10px 0px;
                border: none;
            }

            .stButton > button:hover {
                background-color: #3fa043 !important;
            }

        </style>
    """, unsafe_allow_html=True)

    # CONTENIDO -----------------------------------------------------
    st.markdown("<div class='login-container'>", unsafe_allow_html=True)

    # LOGO CENTRADO
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/logo.png")
    st.markdown("</div>", unsafe_allow_html=True)

    # CAJA DEL LOGIN
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("<h2>Inicio de Sesión</h2>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        if not con:
            st.error("❌ No hay conexión con la base de datos")
            return
        
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
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div></div>", unsafe_allow_html=True)
