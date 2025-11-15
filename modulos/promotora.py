import streamlit as st
from modulos.config.conexion import obtener_conexion

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
        cursor.execute("""
            SELECT g.Id_Grupo, g.Nombre_del_grupo, g.Fecha_de_inicio, g.Tasa_de_intereses
            FROM Grupo g
            INNER JOIN Empleado e ON g.Id_Promotora = e.Id_Empleado
            WHERE e.Usuario = %s
        """, (usuario,))
        grupos = cursor.fetchall()

        if not grupos:
            st.warning("⚠️ No hay grupos asignados a esta promotora.")
        else:
            st.subheader("📋 Grupos bajo supervisión")
            for g in grupos:
                st.write(f"**Nombre:** {g['Nombre_del_grupo']}")
                st.write(f"📅 Fecha de inicio: {g['Fecha_de_inicio']}")
                st.write(f"💰 Tasa de interés: {g['Tasa_de_intereses']}%")
                st.divider()
    except Exception as e:
        st.error(f"Error al consultar los datos: {e}")
    finally:
        con.close()
