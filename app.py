import streamlit as st
from modulos.login import login
from modulos.promotora import interfaz_promotora
from modulos.directiva import interfaz_directiva

# Inicializar variables de sesión
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""
if "rol" not in st.session_state:
    st.session_state["rol"] = ""

# --- MENÚ LATERAL ---
st.sidebar.title("📋 Menú principal")

if st.session_state["sesion_iniciada"]:
    st.sidebar.success(f"Sesión iniciada como: {st.session_state['usuario']} ({st.session_state['rol']})")
    st.sidebar.markdown("---")

    # Depuración (puedes quitar esta línea cuando todo funcione)
    st.sidebar.write(f"🧠 Rol detectado: **{st.session_state['rol']}**")

    # --- RUTA SEGÚN ROL ---
    rol = st.session_state["rol"].strip().lower()

    if rol == "director":
        interfaz_directiva()

    elif rol == "promotora":
        interfaz_promotora()

    elif rol == "admin":
        st.title("🧑‍💻 Panel de Administrador")
        st.info("Este módulo está en desarrollo. Aquí se gestionará el panorama general del sistema.")

    else:
        st.warning("⚠️ Rol no reconocido. Contacta al administrador.")

    # --- CERRAR SESIÓN ---
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""
        st.experimental_rerun()

else:
    login()
