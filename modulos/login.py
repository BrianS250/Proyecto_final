import streamlit as st
from modulos.conexion import obtener_conexion
import base64

# ================================================
# FUNCIÓN PARA CARGAR IMÁGENES BASE64
# ================================================
def load_base64(path):
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def login():

    # Cargar imágenes
    logo = load_base64("modulos/imagenes/logo.png")
    ilustracion = load_base64("modulos/imagenes/ilustracion.png")

    # ============================================
    # ESTILOS PREMIUM REALES (FUNCIONA EN STREAMLIT)
    # ============================================
    st.markdown("""
    <style>

    * { font-family: 'Poppins', sans-serif !important; }

    .stApp {
        background: #F4F5F0 !important;
    }

    /* Imagen izquierda */
    .img-ilustracion {
        width: 95%;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }

    /* Tarjeta */
    .login-card {
        background: white;
        padding: 40px 50px;
        border-radius: 25px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.18);
        width: 420px;
        margin: auto;
        text-align: center;
    }

    /* Logo */
    .logo-img {
        width: 170px;
        margin-bottom: 10px;
    }

    .title {
        font-size: 28px;
        font-weight: 600;
        color: #123A75;
        margin-bottom: 25px;
    }

    /* Inputs */
    .stTextInput>div>div>input {
        background: #FFFFFF !important;
        color: #000000 !important;            /* <-- Texto negro */
        border: 1px solid #7A7A7A !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }

    /* Botón */
    .stButton>button {
        background-color: #6FB43F !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 10px !important;
        height: 50px;
        width: 100%;
        border: none !important;
    }

    .stButton>button:hover {
        background-color: #5A9634 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # ============================================
    # LAYOUT REAL EN COLUMNAS STREAMLIT
    # ============================================
    col1, col2 = st.columns([1.2, 1])

    # Columna izquierda: Ilustración
    with col1:
        st.markdown(
            f"<img src='data:image/png;base64,{ilustracion}' class='img-ilustracion'>",
            unsafe_allow_html=True
        )

    # Columna derecha: Tarjeta de Login
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)

        # Logo
        st.markdown(
            f"<img src='data:image/png;base64,{logo}' class='logo-img'>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='title'>Inicio de Sesión</div>", unsafe_allow_html=True)

        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):
            try:
                con = obtener_conexion()
                cursor = con.cursor(dictionary=True)
                cursor.execute("""
                    SELECT Usuario, Rol
                    FROM Empleado
                    WHERE Usuario = %s AND Contra = %s
                """, (usuario, contraseña))

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
