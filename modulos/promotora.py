import streamlit as st
from modulos.Configuracion.conexion import obtener_conexion

def interfaz_promotora():
    st.header("👩‍💼 Panel de Promotora")
    st.write("Supervisa tus grupos, registra nuevos y valida información financiera.")

    st.subheader("💵 Validar información financiera")
    st.info("Aquí podrás revisar préstamos, pagos y movimientos de los grupos.")
    st.warning("⚠️ Módulo en desarrollo. Pronto podrás aprobar pagos y revisar saldos.")

    # Ejemplo de conexión (opcional)
    try:
        con = obtener_conexion()
        st.success("✅ Conexión establecida con la base de datos.")
        con.close()
    except Exception as e:
        st.error(f"Error al conectar con la base de datos: {e}")
