import streamlit as st
from modulos.conexion import obtener_conexion

def login():
    
    # ===== ESTILO CSS =====
    st.markdown("""
        <style>
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 40px;
        }
        .login-box {
            background-color: #FFFFFF;
            padding: 40px;
            border-radius: 15px;
            width: 420px;
            box-shadow: 0px 4px 25px rgba(0, 0, 0, 0.1);
        }
        label {
            font-weight: 600;
            color: #1a2b49;
        }
        input {
            color: #1a2b49 !important;
        }
        button[kind="primary"] {
            background-color: #3E8E41 !important;
            color: white !important;
            border-radius: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    # ===== DISEÑO =====
    col1, col2 = st.columns([1, 1])

    # Imagen izquierda
    with col1:
        st.image("modulos/imagenes/ilustracion.png", width=420)

    # Formulario
    with col2:
        st.markdown('<div class="login-container"><div class="login-box">', unsafe_allow_html=True)

        st.image("modulos/imagenes/logo.png", width=140)

        st.markdown("## Inicio de Sesión")

        usuario = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Iniciar sesión"):
            con = obtener_conexion()
            if con:
                cursor = con.cursor(dictionary=True)
                cursor.execute(
                    "SELECT Usuario, Rol FROM Empleado WHERE Usuario=%s AND Contra=%s",
                    (usuario, password)
                )
                datos = cursor.fetchone()

                if datos:
                    st.session_state["sesion_iniciada"] = True
                    st.session_state["usuario"] = datos["Usuario"]
                    st.session_state["rol"] = datos["Rol"]
                    st.success("Inicio de sesión exitoso.")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")
            else:
                st.error("No se pudo conectar a la base de datos.")

        st.markdown("</div></div>", unsafe_allow_html=True)
