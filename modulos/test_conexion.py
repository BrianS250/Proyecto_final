import streamlit as st
from modulos.conexion import obtener_conexion

def probar_conexion():
    st.title("🔌 Test de conexión a MySQL (Clever Cloud)")

    con = obtener_conexion()

    if con:
        st.success("✅ Conexión exitosa con Clever Cloud")

        try:
            cursor = con.cursor()
            cursor.execute("SELECT 1;")
            resultado = cursor.fetchone()
            st.write("Resultado de prueba:", resultado)
        except Exception as e:
            st.error(f"⚠️ La conexión se abrió, pero hubo un error al ejecutar una consulta: {e}")
    else:
        st.error("❌ No se pudo conectar. Revisa tus credenciales.")

probar_conexion()


