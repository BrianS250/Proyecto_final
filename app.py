import streamlit as st

from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora
from modulos.administrador import interfaz_admin  # ← LO DESACTIVAMOS PARA EVITAR EL ERROR


# -------------------------------
# ESTADO DE SESIÓN
# -------------------------------

if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if "rol" not in st.session_state:
    st.session_state["rol"] = None


# -------------------------------
# LÓGICA PRINCIPAL
# -------------------------------

if st.session_state["sesion_iniciada"]:

    rol = st.session_state["rol"]

    # DIRECTOR
    if rol == "Director":
        interfaz_directiva()

    # PROMOTORA
    elif rol == "Promotora":
        interfaz_promotora()

     # ADMINISTRADOR
    elif rol == "Administrador":
        interfaz_admin()

    else:
        st.error(f"❌ Rol no reconocido: {rol}")
        st.session_state.clear()
        st.rerun()

    # BOTÓN CERRAR SESIÓN
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

else:
    login()

   
       
