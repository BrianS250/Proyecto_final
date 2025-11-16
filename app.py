if st.session_state["sesion_iniciada"]:
    usuario = st.session_state["usuario"]
    rol = st.session_state["rol"].strip().lower()  # 🔹 Limpia espacios y pone en minúsculas

    st.sidebar.success(f"Sesión iniciada como: {usuario} ({st.session_state['rol']})")
    st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)

    # Normalizamos el rol para comparación
    if rol == "promotora":
        interfaz_promotora()

    elif rol in ["directiva", "director"]:
        interfaz_directiva()

    elif rol == "administrador":
        st.title("🛠️ Panel de Administrador")
        st.info("Visualiza el panorama completo de los distritos y grupos.")
        st.warning("🔧 Este módulo está en desarrollo.")

    else:
        st.warning("⚠️ Rol no reconocido. Contacta al administrador.")
else:
    login()
