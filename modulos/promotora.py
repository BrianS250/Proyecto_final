import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ============================================================
# 🟦 INTERFAZ PRINCIPAL — PROMOTORA
# ============================================================

def interfaz_promotora():
    st.title("👩‍💼 Panel de Promotora")
    st.write("Supervisa grupos, valida información y descarga reportes consolidados.")

    opciones = [
        "Consultar grupos",
        "Validar información financiera",
        "Reportes consolidados"
    ]

    seleccion = st.sidebar.radio("Seleccione una opción:", opciones)

    if seleccion == "Consultar grupos":
        pagina_consultar_grupos()

    elif seleccion == "Validar información financiera":
        pagina_validar_finanzas()

    elif seleccion == "Reportes consolidados":
        pagina_reportes()



# ============================================================
# 📌 CONSULTAR GRUPOS ASIGNADOS
# ============================================================

def pagina_consultar_grupos():
    st.header("📋 Grupos Asignados")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT id_grupo, nombre_grupo, fecha_inicio, periodicidad 
            FROM grupos
            WHERE promotora_asignada = %s
        """, (st.session_state["usuario"],))

        datos = cursor.fetchall()

        if not datos:
            st.warning("No tiene grupos asignados.")
            return

        df = pd.DataFrame(datos, columns=["ID", "Grupo", "Inicio", "Periodicidad"])
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Error al obtener los grupos: {e}")



# ============================================================
# 📌 VALIDACIÓN DE INFORMACIÓN FINANCIERA
# ============================================================

def pagina_validar_finanzas():
    st.header("💵 Validar Información Financiera")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT 
                p.id_prestamo,
                g.nombre_grupo,
                m.nombre,
                p.monto,
                p.interes,
                p.saldo,
                p.estado
            FROM prestamos p
            INNER JOIN miembros m ON p.id_miembro = m.id_miembro
            INNER JOIN grupos g ON m.id_grupo = g.id_grupo;
        """)

        prestamos = cursor.fetchall()

        if not prestamos:
            st.info("No hay préstamos registrados.")
            return

        df = pd.DataFrame(prestamos, columns=[
            "ID", "Grupo", "Miembro", "Monto", "Interés", "Saldo", "Estado"
        ])
        st.dataframe(df, use_container_width=True)

        st.subheader("✔ Validación")
        id_sel = st.number_input("ID de préstamo a validar", min_value=1, step=1)
        decision = st.selectbox("Estado de validación", ["Aprobado", "Rechazado"])

        if st.button("Guardar validación"):
            try:
                cursor.execute("""
                    UPDATE prestamos
                    SET estado_validacion = %s
                    WHERE id_prestamo = %s
                """, (decision, id_sel))
                con.commit()
                st.success("Validación registrada correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al validar: {e}")

    except Exception as e:
        st.error(f"Error al obtener información financiera: {e}")



# ============================================================
# 📌 REPORTES CONSOLIDADOS
# ============================================================

def pagina_reportes():
    st.header("📊 Reportes Consolidados del Distrito")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT
                g.nombre_grupo,
                COUNT(m.id_miembro) AS miembros,
                SUM(a.monto) AS ahorro_total,
                SUM(p.saldo) AS prestamos_pendientes
            FROM grupos g
            LEFT JOIN miembros m ON g.id_grupo = m.id_grupo
            LEFT JOIN ahorros a ON g.id_grupo = a.id_grupo
            LEFT JOIN prestamos p ON g.id_grupo = p.id_grupo
            GROUP BY g.id_grupo;
        """)

        reporte = cursor.fetchall()

        if not reporte:
            st.warning("No hay datos para generar reporte.")
            return

        df = pd.DataFrame(reporte, columns=[
            "Grupo", "Miembros", "Ahorro Total", "Préstamos Pendientes"
        ])

        st.dataframe(df, use_container_width=True)

        # Descarga Excel
        st.subheader("⬇ Descargar reporte")
        excel = df.to_excel("reporte_distrito.xlsx", index=False)
        with open("reporte_distrito.xlsx", "rb") as f:
            st.download_button(
                "Descargar Excel",
                f,
                file_name="Reporte_Consolidado.xlsx"
            )

    except Exception as e:
        st.error(f"Error al generar reportes: {e}")
