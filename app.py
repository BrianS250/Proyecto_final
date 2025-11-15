import streamlit as st
from modulos.login import login, mostrar_interfaz_unica
from modulos.venta import mostrar_venta  # 🛒 Importamos el módulo de ventas

# -------------------------------------------------------------
# 🎯 APLICACIÓN PRINCIPAL
# -------------------------------------------------------------
if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
    st.sidebar.title("📋 Menú principal")
    st.sidebar.button("Cerrar sesión", on_click=lambda: st.session_state.clear())

    # Opciones del menú lateral
    opciones = ["Registro de Ventas", "Otra opción"]
    seleccion = st.sidebar.selectbox("Selecciona una opción", opciones)

    # Mostrar la opción elegida
    if seleccion == "Registro de Ventas":
        mostrar_venta()
    elif seleccion == "Otra opción":
        st.write("🚧 Esta sección estará disponible próximamente.")
else:
    login()



