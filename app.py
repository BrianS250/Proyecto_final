# app.py
import streamlit as st
from modulos.login import login
from modulos.venta import mostrar_venta

# Verificamos si la sesión ya está iniciada
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    st.sidebar.title("Menú principal")
    opciones = ["Ventas", "Cerrar sesión"]
    seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)

    if seleccion == "Ventas":
        mostrar_venta()

    elif seleccion == "Cerrar sesión":
        st.session_state["sesion_iniciada"] = False
        st.success("Sesión cerrada correctamente.")
        st.rerun()

else:
    # Mostrar el login si no hay sesión activa
    login()


