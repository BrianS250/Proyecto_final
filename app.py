import streamlit as st
from modulos.login import login, mostrar_interfaz_unica

if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    st.sidebar.title("📋 Menú principal")
    st.sidebar.button("Cerrar sesión", on_click=lambda: st.session_state.clear())
    mostrar_interfaz_unica()
else:
    login()



