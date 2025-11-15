import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

# --------------------------------------------------------
# 👩‍💼 PANEL PRINCIPAL DE PROMOTORA
# --------------------------------------------------------
def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora")
    st.write(f"Bienvenida, {st.session_state['usuario']}")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor(dictionary=True)

    # Menú lateral
    opcion = st.sidebar.radio(
        "Seleccione una opción",
        ("🏠 Grupos asignados", "💰 Resumen financiero", "⬇️ Reporte consolidado")
    )

    # --------------------------------------------------------
    # 1️⃣ GRUPOS ASIGNADOS
    # --------------------------------------------------------
    if opcion == "🏠 Grupos asignados":
        st.subheader("👥 Grupos bajo su supervisión")
        try:
            query = """
                SELECT Id_Grupo, NombreGrupo, FechaInicio, TasaInteres, 
                       PeriodicidadReuniones, TipoMulta
                FROM Grupo 
                WHERE Id_Promotora = %s
            """
            cursor.execute(query, (st.session_state["id_usuario"],))
            grupos = cursor.fetchall()

            if grupos:
                st.dataframe(pd.DataFrame(grupos))
            else:
                st.info("No tiene grupos asignados actualmente.")
        except Exception as e:
            st.error(f"⚠️ Error al cargar los grupos: {e}")

    # --------------------------------------------------------
    # 2️⃣ RESUMEN FINANCIERO
    # --------------------------------------------------------
    elif opcion == "💰 Resumen financiero":
        st.subheader("💰 Información financiera consolidada")

        try:
            query_finanzas = """
                SELECT g.NombreGrupo,
                       COALESCE(SUM(a.Monto), 0) AS TotalAhorros,
                       COALESCE(SUM(p.Monto), 0) AS TotalPrestamos
                FROM Grupo g
                LEFT JOIN Ahorro a ON g.Id_Grupo = a.Id_Grupo
                LEFT JOIN Prestamo p ON g.Id_Grupo = p.Id_Grupo
                WHERE g.Id_Promotora = %s
                GROUP BY g.Id_Grupo, g.NombreGrupo
            """
            cursor.execute(query_finanzas, (st.session_state["id_usuario"],))
            resumen = cursor.fetchall()

            if resumen:
                df = pd.DataFrame(resumen)
                st.dataframe(df)
            else:
                st.info("No se encontró información financiera disponible.")
        except Exception as e:
            st.error(f"⚠️ Error al generar resumen: {e}")

    # --------------------------------------------------------
    # 3️⃣ REPORTE CONSOLIDADO DESCARGABLE
    # --------------------------------------------------------
    elif opcion == "⬇️ Reporte consolidado":
        st.subheader("📊 Generar y descargar reporte general")

        try:
            query_reporte = """
                SELECT g.NombreGrupo, d.Nombre AS Distrito,
                       COALESCE(SUM(a.Monto), 0) AS TotalAhorros,
                       COALESCE(SUM(p.Monto), 0) AS TotalPrestamos,
                       COUNT(DISTINCT r.Id_Reunion) AS Reuniones
                FROM Grupo g
                LEFT JOIN Ahorro a ON g.Id_Grupo = a.Id_Grupo
                LEFT JOIN Prestamo p ON g.Id_Grupo = p.Id_Grupo
                LEFT JOIN Reunion r ON g.Id_Grupo = r.Id_Grupo
                LEFT JOIN Distrito d ON g.Id_Distrito = d.Id_Distrito
                WHERE g.Id_Promotora = %s
                GROUP BY g.Id_Grupo
            """
            cursor.execute(query_reporte, (st.session_state["id_usuario"],))
            data = cursor.fetchall()

            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)

                # Botón de descarga CSV
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Descargar reporte en CSV",
                    data=csv,
                    file_name="Reporte_Promotora.csv",
                    mime="text/csv"
                )
            else:
                st.info("No hay datos disponibles para el reporte.")
        except Exception as e:
            st.error(f"⚠️ Error al generar el reporte: {e}")

    con.close()
