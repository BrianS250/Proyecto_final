import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ============================================
    # TIPOGRAFÍA
    # ============================================
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # ============================================
    # ESTILOS GENERALES
    # ============================================
    st.markdown("""
    <style>

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    .stApp {
        background-color: #F5F5F0 !important; /* color crema del mockup */
        padding: 0 !important;
    }

    /* Ajustar ancho total */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 1500px !important;
    }

    /* LAYOUT DOS COLUMNAS */
    .two-col {
        display: grid;
        grid-template-columns: 55% 45%;
        height: 100vh;
        align-items: center;
    }

    /* IMAGEN IZQUIERDA */
    .left-img {
        width: 85%;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }

    /* TARJETA LOGIN */
    .login-card {
        background-color: white;
        padding: 50px 55px;
        border-radius: 20px;
        width: 420px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
    }

    /* LOGO */
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 180px;
        margin-bottom: 10px;
    }

    /* TITULO */
    .title {
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        color: #123A75;
        margin-bottom: 25px;
    }

    /* INPUTS */
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        border-radius: 10px !important;
        border: 1px solid #D8D8D8 !important;
        padding: 12px !important;
        font-size: 15px !important;
    }

    /* BOTON VERDE CVX */
    .stButton>button {
        width: 100%;
        background-color: #6FB43F !important;
        border-radius: 10px !important;
        border: none;
        height: 50px;
        font-size: 18px !important;
        font-weight: 600 !important;
        color: white !important;
        margin-top: 14px;
    }

    .stButton>button:hover {
        background-color: #5A9634 !important;
        transform: scale(1.02);
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # LAYOUT EXACTO DEL MOCKUP
    # ============================================
    st.markdown("<div class='two-col'>", unsafe_allow_html=True)

    # Columna izquierda - ilustración
    st.markdown("""
        <div>
            <img src='modulos/imagenes/ilustracion.png' class='left-img'>
        </div>
    """, unsafe_allow_html=True)

    # Columna derecha - tarjeta login
    st.markdown("<div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<img src='modulos/imagenes/logo.png' class='logo'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>Inicio de Sesión</div>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
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
            st.success("Bienvenido ✔")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
