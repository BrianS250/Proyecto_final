import streamlit as st
from modulos.conexion import obtener_conexion

def login():

    # ========================== ESTILOS CSS ==========================
    st.markdown(
        """
        <style>

        /* Fondo general */
        .main {
            background: linear-gradient(135deg, #E8F5E9 0%, #FFFFFF 100%);
            animation: fadeIn 1.2s ease-in-out;
        }

        /* Animación suave */
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }

        /* Caja del login */
        .login-box {
            background-color: rgba(255, 255, 255, 0.95);
            padding: 30px 35px;
            border-radius: 18px;
            box-shadow: 0 4px 18px rgba(0, 0, 0, 0.12);
            animation: fadeIn 1.8s ease;
        }

        .title-text {
            color: #2E7D32;
            font-weight: 800;
            text-align: center;
            font-size: 32px;
        }

        .subtitle-text {
            text-align: center;
            color: #555555;
            font-size: 16px;
            margin-bottom: 10px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ========================== DISEÑO EN COLUMNAS ==========================
    col1, col2 = st.columns([1.2, 2])

    # --------- COLUMNA IZQUIERDA: LOGO ----------
    with col1:
        st.image("logo_cvx.png", width=230)

    # --------- COLUMNA DERECHA: FORMULARIO ----------
    with col2:
        st.markdown("<p class='title-text'>Solidaridad CVX</p>", unsafe_allow_html=True)
        st.markdown(
            "<p class='subtitle-text'>Sistema de Gestión Comunitaria</p>",
            unsafe_allow_html=True
        )

        st.markdown("<div class='login-box'>", unsafe_allow_html=True)

        usuario = st.text_input("Usuario", placeholder="Ingrese su usuario")

        # ------- CONTRASEÑA CON BOTÓN MOSTRAR -------
        mostrar = st.checkbox("Mostrar contraseña")
        tipo_contra = "text" if mostrar else "password"

        contra = st.text_input("Contraseña", type=tipo_contra, placeholder="Ingrese su contraseña")

        # ========================== BOTÓN LOGIN ==========================
        if st.button("Iniciar sesión", use_container_width=True):
            if usuario.strip() == "" or contra.strip() == "":
                st.warning("⚠️ Debe ingresar usuario y contraseña.")
                st.markdown("</div>", unsafe_allow_html=True)
                return

            con = obtener_conexion()
            if not con:
                st.error("❌ Error: No se pudo conectar a la base de datos.")
                st.markdown("</div>", unsafe_allow_html=True)
                return

            try:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT Usuario, Contra, Rol FROM Empleado WHERE Usuario = %s",
                    (usuario,)
                )
                datos = cursor.fetchone()

                if datos:
                    usuario_db, contra_db, rol_db = datos

                    if contra == contra_db:
                        st.success(f"✨ Bienvenido, **{usuario_db}**")

                        st.session_state["session_iniciada"] = True
                        st.session_state["usuario"] = usuario_db
                        st.session_state["rol"] = rol_db

                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta.")

                else:
                    st.error("❌ Usuario no encontrado.")

            except Exception as e:
                st.error("⚠️ Error procesando el inicio de sesión.")
                print(e)

        st.markdown("</div>", unsafe_allow_html=True)

    # ========================== IMAGEN FINAL ==========================
    st.write("")
    st.image("comunidad_cvx.png", use_column_width=True)
