import streamlit as st
from modulos.config.conexion import obtener_conexion
from modulos.venta import mostrar_venta  # ✅ sin espacio

def verificar_usuario(Usuario, Contra):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None
    else:
        st.session_state["conexion_exitosa"] = True

    try:
        cursor = con.cursor()
        query = "SELECT Usuario, Contra FROM Empleados WHERE Usuario = %s AND Contra = %s"
        cursor.execute(query, (Usuario, Contra))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None
    finally:
        con.close()


def login():
    if "sesion_iniciada" not in st.session_state:
        st.session_state["sesion_iniciada"] = False

    st.title("🔐 Inicio de Sesión - SGI")

    if st.session_state.get("conexion_exitosa"):
        st.success("✅ Conexión a la base de datos establecida correctamente.")

    Usuario = st.text_input("Usuario", key="Usuario_input")
    Contra = st.text_input("Contraseña", type="password", key="Contra_input")

    if st.button("Iniciar sesión"):
        tipo = verificar_usuario(Usuario, Contra)
        if tipo:
            st.session_state["usuario"] = Usuario
            st.session_state["tipo_usuario"] = tipo
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido, {Usuario} 👋")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")
