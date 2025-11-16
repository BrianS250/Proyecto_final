import streamlit as st
from modulos.login import login
from modulos.promotora import interfaz_promotora
from modulos.directiva import interfaz_directiva
from modulos.admin import interfaz_admin  # si aún no existe, puedes crear un placeholder

# ------------------------------------------------------------
# FUNCIÓN PARA CERRAR SESIÓN
# ------------------------------------------------------------
def cerrar_sesion():
    st.session_state["sesion_iniciada"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()

# ------------------------------------------------------------
# APP PRINCIPAL
# ------------------------------------------------------------
def main():
    st.sidebar.title("📋 Menú principal")

    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False

    if st.session_state["sesion_iniciada"]:
        usuario = st.session_state["usuario"]
        rol = st.session_state["rol"]

        st.sidebar.success(f"Sesión iniciada como: {usuario} ({rol})")
        st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)

        # Mostrar panel según el rol
        if rol == "Promotora":
            interfaz_promotora()
        elif rol == "Directiva":
            interfaz_directiva()
        elif rol == "Administrador":
            interfaz_admin()
        else:
            st.warning("⚠️ Rol no reconocido. Contacta al administrador.")
    else:
        login()

if __name__ == "__main__":
    main()
