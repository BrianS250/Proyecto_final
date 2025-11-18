import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva

# ---------------------------------------------------
# ESTADO DE SESIÓN PARA CONTROLAR LOGIN / LOGOUT
# ---------------------------------------------------

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

# ---------------------------------------------------
# MOSTRAR PANTALLA SEGÚN SESIÓN
# ---------------------------------------------------

if st.session_state["sesion_iniciada"]:
    # Si la sesión está activa -> cargar menú de directiva
    interfaz_directiva()
else:
    # Si no ha iniciado sesión -> mostrar login
    login()
