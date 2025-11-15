import streamlit as st
from modulos.config.conexion import obtener_conexion
from datetime import date
import pandas as pd

def panel_promotora(id_promotora):
    st.title("👩‍💼 Panel de Promotora")
    st.markdown("Consulta y supervisa los grupos bajo tu responsabilidad.")

    opcion = st.sidebar.radio("Selecciona una opción:", 
                              ["📁 Consultar grupos", 
                               "💵 Validar información financiera", 
                               "📊 Reportes consolidados"])

    if opcion == "📁 Consultar grupos":
        mostrar_grupos(id_promotora)
    elif opcion == "💵 Validar información financiera":
        validar_finanzas(id_promotora)
    elif opcion == "📊 Reportes consolidados":
        generar_reportes(id_promotora)


# --------------------------
# SECCIÓN 1: CONSULTAR GRUPOS
# --------------------------
def mostrar_grupos(id_promotora):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)
    cur.execute("SELECT * FROM Grupo WHERE Id_Promotora = %s", (id_promotora,))
    grupos = cur.fetchall()
    cur.close()
    con.close()

    st.subheader("📋 Grupos Asignados")
    for g in grupos:
        with st.expander(f"📌 {g['Nombre_grupo']}"):
            st.write(f"**Tasa de interés:** {g['Tasa_de_interes']}%")
            st.write(f"**Periodicidad:** {g['Periodicidad_de_reuniones']}")
            st.write(f"**Tipo de multa:** {g['Tipo_de_multa']}")
            st.write(f"**Reglas:** {g['Reglas_de_prestamo']}")
            st.write(f"**Fecha de inicio:** {g['fecha_inicio']}")
            st.write(f"**Distrito:** {g['Id_Distrito']}")


# --------------------------
# SECCIÓN 2: VALIDAR FINANZAS
# --------------------------
def validar_finanzas(id_promotora):
    st.subheader("💵 Validar información financiera")
    st.info("Aquí podrás revisar los préstamos, pagos y reportes de cada grupo.")

    # Aquí luego se integrará la validación real de pagos.
    st.warning("⚠️ Módulo en desarrollo (próximamente permitirá aprobar pagos y verificar saldos).")


# --------------------------
# SECCIÓN 3: REPORTES CONSOLIDADOS
# --------------------------
def generar_reportes(id_promotora):
    st.subheader("📊 Reporte Consolidado")
    st.write("Descarga los datos de todos los grupos que supervisas.")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT Nombre_grupo, fecha_inicio, Tasa_de_interes, Periodicidad_de_reuniones, 
               Tipo_de_multa, Reglas_de_prestamo, Id_Distrito
        FROM Grupo WHERE Id_Promotora = %s
    """, (id_promotora,))
    grupos = cur.fetchall()
    cur.close()
    con.close()

    if grupos:
        df = pd.DataFrame(grupos)
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "📥 Descargar reporte en Excel",
            data=df.to_excel(index=False, sheet_name="Grupos", engine="openpyxl"),
            file_name=f"reporte_grupos_promotora_{id_promotora}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("No hay grupos asignados para mostrar.")
