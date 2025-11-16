import streamlit as st
from modulos.login import login
from modulos.directiva import interfaz_directiva
from modulos.promotora import interfaz_promotora

# Verificar si hay sesión activa
if "sesion_iniciada" not in st.session_state:
    st.session_state["sesion_iniciada"] = False

if not st.session_state["sesion_iniciada"]:
    login()
else:
    st.sidebar.title("📋 Menú principal")
    st.sidebar.success(f"Sesión iniciada como: {st.session_state['rol']} ({st.session_state['usuario']})")

    # Redirigir según el rol
    rol = st.session_state["rol"].lower()
    if rol == "director":
        interfaz_directiva()
    elif rol == "promotora":
        interfaz_promotora()
    else:
        st.warning("⚠️ Rol no reconocido. Contacta al administrador.")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.experimental_rerun()
