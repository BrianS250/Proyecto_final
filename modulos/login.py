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
    # ESTILOS PREMIUM
    # ============================================
    st.markdown("""
    <style>

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    /* Fondo completo */
    .stApp {
        background: linear-gradient(180deg, #F5F6F2 0%, #EEEFEA 100%) !important;
        padding: 0 !important;
    }

    /* Contenedor general sin padding */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 1600px !important;
    }

    /* GRID DOS COLUMNAS */
    .two-col {
        display: grid;
        grid-template-columns: 50% 50%;
        height: 100vh;
        align-items: center;
        padding-left: 30px;
        padding-right: 30px;
    }

    /* IMAGEN IZQUIERDA PREMIUM */
    .left-img {
        width: 90%;
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 22px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.18);
        transition: all 0.3s ease-in-out;
    }

    .left-img:hover {
        transform: scale(1.01);
        box-shadow: 0 25px 55px rgba(0,0,0,0.22);
    }

    /* TARJETA LOGIN – estilo iPad */
    .login-card {
        background: #FFFFFF;
        padding: 55px 60px 60px 60px;
        border-radius: 26px;
        width: 430px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 18px 45px rgba(0,0,0,0.18);
        transition: all 0.25s ease-in-out;
        border: 1px solid rgba(0,0,0,0.05);
    }

    .login-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 25px 60px rgba(0,0,0,0.22);
    }

    /* LOGO */
    .logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 190px;
        margin-bottom: 12px;
    }

    /* TÍTULO */
    .title {
        text-align: center;
        font-size: 30px;
        font-weight: 600;
        color: #123A75;
        margin-bottom: 30px;
    }

    /* INPUTS */
    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        border: 1px solid #C7D0DA !important;
        padding: 14px !important;
        font-size: 15px !important;
        transition: all 0.3s ease-in-out;
    }

    .stTextInput>div>div>input:focus {
        border: 1px solid #6FB43F !important;
        box-shadow: 0 0 0 3px rgba(111,180,63,0.20) !important;
    }

    /* BOTÓN VERDE CVX PREMIUM */
    .stButton>button {
        width: 100%;
        background-color: #6FB43F !important;
        border-radius: 12px !important;
        border: none !important;
        height: 52px !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        margin-top: 18px;
        box-shadow: 0 6px 14px rgba(111,180,63,0.25);
        transition: all 0.2s ease-in-out;
    }

    .stButton>button:hover {
        background-color: #5A9634 !important;
        transform: translateY(-2px);
        box-shadow: 0 10px 22px rgba(111,180,63,0.32);
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # LAYOUT REAL DEL MOCKUP PREMIUM
    # ============================================
    st.markdown("<div class='two-col'>", unsafe_allow_html=True)

    # COLUMNA IZQUIERDA
    st.markdown("""
        <div>
            <img src='modulos/imagenes/ilustracion.png' class='left-img'>
        </div>
    """, unsafe_allow_html=True)

    # COLUMNA DERECHA – TARJETA LOGIN
    st.markdown("<div>", unsafe_allow_html=True)

    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<img src='modulos/imagenes/logo.png' class='logo'>", unsafe_allow_html=True)

    st.markdown("<div class='title'>Inicio de Sesión</div>", unsafe_allow_html=True)

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        try:
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
        except Exception as e:
            st.error(f"Error en login: {e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
