import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ============================
    # FUENTE
    # ============================
    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    # ============================
    # ESTILOS
    # ============================
    st.markdown("""
    <style>

    * {
        font-family: 'Poppins', sans-serif !important;
    }

    .stApp {
        background-color: #F7F9FC !important;
    }

    /* Contenedor general (lado izq + login derecha) */
    .layout {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 40px;
    }

    /* Panel ilustración */
    .left-box {
        width: 45%;
        text-align: center;
        padding-right: 20px;
    }

    .left-img {
        width: 90%;
        border-radius: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.10);
    }

    /* Tarjeta login */
    .login-card {
        width: 380px;
        background: white;
        padding: 40px 45px 50px 45px;
        border-radius: 22px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.12);
        margin-left: 25px;
    }

    /* Logo */
    .logo-box {
        text-align: center;
        margin-bottom: 10px;
    }

    /* Título */
    .title {
        text-align: center;
        font-size: 28px;
        font-weight: 600;
        color: #123A75;
        margin-bottom: 25px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background-color: #FDFEFF !important;
        border-radius: 10px !important;
        border: 1px solid #D0D7E2 !important;
        padding: 12px !important;
        font-size: 15px !important;
    }

    /* Botón */
    .stButton>button {
        width: 100%;
        background-color: #6FB43F !important;
        border-radius: 10px !important;
        border: none !important;
        height: 48px;
        color: white !important;
        font-size: 18px !important;
        font-weight: 600;
        margin-top: 15px;
    }

    .stButton>button:hover {
        background-color: #5A9634 !important;
        transform: scale(1.02);
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================
    # DISEÑO EN PANTALLA DIVIDIDA
    # ============================
    st.markdown("<div class='layout'>", unsafe_allow_html=True)

    # Panel ilustración
    st.markdown("<div class='left-box'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/ilustracion.png", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Panel login
    st.markdown("<div class='login-card'>", unsafe_allow_html=True)

    st.markdown("<div class='logo-box'>", unsafe_allow_html=True)
    st.image("modulos/imagenes/logo.png", width=165)
    st.markdown("</div>", unsafe_allow_html=True)

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

