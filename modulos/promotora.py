import streamlit as st
from modulos.config.conexion import obtener_conexion

# ---------------------------------------------------------
# Interfaz principal del rol Promotora
# ---------------------------------------------------------
def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora")

    usuario = st.session_state.get("usuario", "Desconocido")
    st.sidebar.success(f"Sesión iniciada: {usuario} (Promotora)")

    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return

    try:
        cursor = con.cursor(dictionary=True)

        # Buscar el ID de la promotora según su usuario
        cursor.execute("SELECT Id_Empleado FROM Empleado WHERE Usuario = %s", (usuario,))
        promotora = cursor.fetchone()

        if not promotora:
            st.warning("No se encontró información de esta promotora.")
            return

        id_promotora = promotora["Id_Empleado"]

        # Consultar los grupos supervisados por esta promotora
        cursor.execute("""
            SELECT Id_Grupo, Nombre_del_grupo, Fecha_de_inicio, Tasa_de_intereses,
                   Periodicidad_de_reuniones, Tipo_de_multa
            FROM Grupo
            WHERE Id_Promotora = %s
        """, (id_promotora,))
        grupos = cursor.fetchall()

        if not grupos:
            st.info("No hay grupos asignados a esta promotora.")
        else:
            st.subheader("📋 Grupos bajo tu supervisión")
            for grupo in grupos:
                with st.expander(f"👥 {grupo['Nombre_del_grupo']}"):
                    st.write(f"**ID del grupo:** {grupo['Id_Grupo']}")
                    st.write(f"**Fecha de inicio:** {grupo['Fecha_de_inicio']}")
                    st.write(f"**Tasa de interés:** {grupo['Tasa_de_intereses']}%")
                    st.write(f"**Periodicidad:** {grupo['Periodicidad_de_reuniones']}")
                    st.write(f"**Tipo de multa:** {grupo['Tipo_de_multa']}")

            st.markdown("---")
            if st.button("📤 Descargar reporte consolidado"):
                st.success("✅ Función de descarga disponible próximamente.")

    except Exception as e:
        st.error(f"❌ Error al cargar grupos: {e}")
    finally:
        con.close()
