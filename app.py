import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora

# ============================
# DESACTIVAR SIDEBAR
# ============================
st.set_page_config(
    page_title="Solidaridad CVX",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================
# ESTADO DE SESIÓN
# ============================
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None

# ============================
# SIN TÍTULOS, SIN SIDEBAR, SIN NADA EXTRA
# ============================

if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]

    if rol == "Directora":
        interfaz_directiva()

    elif rol == "Promotora":
        interfaz_promotora()

    else:
        st.error("Rol no reconocido.")
        st.session_state.clear()
        st.rerun()

else:
    login()
