import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora

# ============================
# ESTADO DE SESIÓN
# ============================
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None

# ============================
# LÓGICA PRINCIPAL
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
