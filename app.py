import streamlit as st

from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora
from modulos.administrador import interfaz_admin  # si existe


# -------------------------------
# ESTADOS DE SESIÓN
# -------------------------------

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None


# -------------------------------
# LÓGICA PRINCIPAL
# -------------------------------

if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]  # ← tal cual viene de BD

    # DIRECTOR = panel de directiva
    if rol == "Director":
        interfaz_directiva()

    # PROMOTORA = panel de promotora
    elif rol == "Promotora":
        interfaz_promotora()

    # ADMINISTRADOR
    elif rol == "Administrador":
        interfaz_admin()

    else:
        st.error(f"❌ Rol no reconocido por el sistema: {rol}")
        st.session_state.clear()
        st.rerun()

    # Cerrar sesión
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

else:
    login()
