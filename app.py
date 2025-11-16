import streamlit as st
from modulos.login import login
from modulos.promotora import interfaz_promotora
from modulos.directiva import interfaz_directiva

# ---------------------------------------------------------
# 🔒 FUNCIÓN PARA CERRAR SESIÓN
# ---------------------------------------------------------
def cerrar_sesion():
    st.session_state["sesion_iniciada"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()

# ---------------------------------------------------------
# 🚀 FUNCIÓN PRINCIPAL
# ---------------------------------------------------------
def main():
    st.sidebar.title("📋 Menú principal")

    # Inicializar variables de sesión
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False
        st.session_state["usuario"] = ""
        st.session_state["rol"] = ""

    # Si la sesión ya está iniciada
    if st.session_state["sesion_iniciada"]:
        usuario = st.session_state["usuario"]
        rol = st.session_state["rol"]

        # Mostrar información del usuario actual
        st.sidebar.success(f"Sesión iniciada como: {usuario} ({rol})")
        st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)

        # ---------------------------------------------------------
        # 👩‍💼 PANEL SEGÚN ROL
        # ---------------------------------------------------------
        st.sidebar.markdown("---")
        st.sidebar.caption(f"🧠 Rol detectado (depuración): '{rol}'")

        if rol.lower() == "promotora":
            interfaz_promotora()

        elif rol.lower() == "director":
            interfaz_directiva()

        else:
            st.warning("⚠️ Rol no reconocido. Contacta al administrador.")

    # Si la sesión no está iniciada, mostrar login
    else:
        login()

# ---------------------------------------------------------
# 🔁 EJECUCIÓN PRINCIPAL
# ---------------------------------------------------------
if __name__ == "__main__":
    main()
