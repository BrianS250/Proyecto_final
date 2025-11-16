import streamlit as st
from modulos.login import login
from modulos.promotora import interfaz_promotora
from modulos.directiva import interfaz_directiva

# --------------------------------------------------
# 🚪 FUNCIÓN PARA CERRAR SESIÓN
# --------------------------------------------------
def cerrar_sesion():
    st.session_state["sesion_iniciada"] = False
    st.session_state["usuario"] = ""
    st.session_state["rol"] = ""
    st.rerun()

# --------------------------------------------------
# 🏠 APLICACIÓN PRINCIPAL
# --------------------------------------------------
def main():
    st.sidebar.title("📋 Menú principal")

    # Inicializar variables de sesión si no existen
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False
    if "rol" not in st.session_state:
        st.session_state["rol"] = ""

    # Si la sesión está iniciada → mostrar panel según rol
    if st.session_state["sesion_iniciada"]:
        usuario = st.session_state["usuario"]
        rol_original = st.session_state["rol"]
        rol = rol_original.strip().lower()  # Normaliza texto

        # Información visible en barra lateral
        st.sidebar.success(f"Sesión iniciada como: {usuario} ({rol_original})")
        st.sidebar.write(f"🧠 Rol detectado (depuración): '{rol}'")  # 👈 Depuración temporal
        st.sidebar.button("Cerrar sesión", on_click=cerrar_sesion)

        # --------------------------------------------------
        # Panel según rol detectado
        # --------------------------------------------------
        if rol == "promotora":
            interfaz_promotora()

        elif rol in ["director", "directora", "directivo", "directiva"]:
            interfaz_directiva()

        elif rol == "administrador":
            st.title("🛠️ Panel de Administrador")
            st.info("Visualiza el panorama completo de los distritos y grupos.")
            st.warning("🔧 Este módulo está en desarrollo.")

        else:
            st.warning("⚠️ Rol no reconocido. Contacta al administrador.")

    else:
        # Si no hay sesión → mostrar login
        login()

# --------------------------------------------------
# 🚀 EJECUCIÓN PRINCIPAL
# --------------------------------------------------
if __name__ == "__main__":
    main()
