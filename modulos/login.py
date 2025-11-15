import streamlit as st

# --- Configuración de credenciales (puedes conectarlo a una BD) ---
usuarios = {
    "admin": "1234",
    "brandon": "5678"
}

# --- Función de autenticación ---
def login(usuario, contrasena):
    if usuario in usuarios and usuarios[usuario] == contrasena:
        return True
    return False

# --- Interfaz de Streamlit ---
st.title("🔐 Sistema de Login con Streamlit")

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.subheader("Iniciar sesión")

    usuario = st.text_input("Usuario")
    contrasena = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        if login(usuario, contrasena):
            st.session_state.autenticado = True
            st.success("✅ ¡Acceso concedido!")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
else:
    st.success(f"Bienvenido ✅")
    st.write("Contenido secreto o menú principal aquí...")
    
    if st.button("Cerrar sesión"):
        st.session_state.autenticado = False
        st.rerun()
