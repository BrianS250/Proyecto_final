import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ============================
    #       ESTILOS CSS
    # ============================
    st.markdown("""
        <style>

            /* Fondo decorativo con ondas */
            .stApp {
                background: #0e1117 !important;
                background-image:
                    radial-gradient(circle at 20% 20%, rgba(0,150,0,0.08) 0%, transparent 60%),
                    radial-gradient(circle at 80% 80%, rgba(100,200,255,0.08) 0%, transparent 60%),
                    url('https://raw.githubusercontent.com/AmilcarRodriguez44/assets/main/ondas-dark.svg');
                background-size: cover;
                background-repeat: no-repeat;
            }

            /* Importar tipografía */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

            html, body, * {
                font-family: 'Poppins', sans-serif !important;
            }

            /* Ocultar cuadro superior molesto */
            .st-emotion-cache-1dp5vir, .st-emotion-cache-1m2q0ib {
                display: none !important;
            }

            .container {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 5vh;
            }

            .logo-container img {
                width: 150px;
                margin: 0 auto;
                display: block;
                filter: brightness(0.85);
            }

            .login-box {
                background: rgba(22, 26, 35, 0.92);
                padding: 30px;
                border-radius: 18px;
                width: 90%;
                max-width: 380px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                margin-top: 20px;
                backdrop-filter: blur(6px);
            }

            h2 {
                color: #e3e6ed !important;
                text-align: center;
                font-weight: 600;
            }

            /* Inputs */
            .stTextInput > div > div > input {
                background-color: #1f2430 !important;
                color: #ffffff !important;
                border: 1px solid #3d4352 !important;
                padding-left: 38px !important;
                border-radius: 8px;
                font-size: 15px;
            }

            /* Iconos dentro del input */
            .icon {
                position: relative;
                top: -36px;
                left: 10px;
                color: #9aa0ad;
                font-size: 18px;
            }

            /* Botón */
            .stButton > button {
                width: 100%;
                background-color: #2e7d32 !important;
                color: white;
                font-size: 16px;
                font-weight: 600;
                padding: 10px;
                border-radius: 8px;
                border: none;
            }

            .stButton > button:hover {
                background-color: #42a043 !important;
            }

        </style>
    """, unsafe_allow_html=True)

    # ============================
    #         CONTENIDO
    # ============================

    st.markdown("<div class='container'>", unsafe_allow_html=True)

    # LOGO CENTRADO
    st.markdown("<div class='logo-container'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/logo.png")
    st.markdown("</div>", unsafe_allow_html=True)

    # CAJA DEL LOGIN
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)
    st.markdown("<h2>Inicio de Sesión</h2>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    st.markdown("<div class='icon'>👤</div>", unsafe_allow_html=True)

    password = st.text_input("Contraseña", type="password")
    st.markdown("<div class='icon'>🔒</div>", unsafe_allow_html=True)

    if st.button("Iniciar sesión"):
        con = obtener_conexion()
        if not con:
            st.error("❌ No se pudo conectar a la base de datos.")
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
