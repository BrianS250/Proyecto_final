import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ============================
    #   ESTILO OSCURO PERSONALIZADO
    # ============================
    st.markdown("""
        <style>
            body {
                background-color: #0e1117 !important;
            }

            .login-box {
                background-color: #161a23;
                padding: 35px;
                width: 420px;
                margin: auto;
                margin-top: 50px;
                border-radius: 18px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.4);
            }

            label, h2, p, .stTextInput > div > div > input {
                color: #e3e6ed !important;
                font-size: 16px;
            }

            /* Input boxes */
            .stTextInput > div > div > input {
                background-color: #1f2430 !important;
                color: #e3e6ed !important;
                border: 1px solid #3b4252 !important;
                padding: 8px;
                border-radius: 6px;
            }

            /* Button */
            .stButton > button {
                background-color: #2e7d32;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 10px 20px;
                width: 100%;
                border: none;
                transition: 0.2s;
            }

            .stButton > button:hover {
                background-color: #41a447;
                color: white;
            }

            /* Ocultar header y menú */
            header, footer, .st-emotion-cache-18ni7ap {
                visibility: hidden;
            }
        </style>
    """, unsafe_allow_html=True)

    # ============================
    #   LOGO CENTRADO
    # ============================
    st.markdown("<div style='text-align:center; margin-top:20px;'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/logo.png", width=150)
    st.markdown("</div>", unsafe_allow_html=True)

    # ============================
    #   CONTENEDOR DEL LOGIN
    # ============================
    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center;'>Inicio de Sesión</h2>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

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

    st.markdown("</div>", unsafe_allow_html=True)
