import streamlit as st
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion
from modulos.reglas_utils import obtener_reglas


# ============================================================
# REPORTE DE CAJA COMPLETO
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ CICLO – LEER DESDE reglas_internas
    # ============================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ Debes registrar las reglas internas primero.")
        return

    ciclo_inicio = reglas.get("ciclo_inicio")
    ciclo_fin = reglas.get("ciclo_fin")

    if not ciclo_inicio:
        st.error("⚠ Falta la fecha de inicio del ciclo en reglas internas.")
        return

    # ============================================================
    # 2️⃣ CREAR REUNIÓN HOY SI NO EXISTE
    # ============================================================
    hoy = date.today().strftime("%Y-%m-%d")
    obtener_o_crear_reunion(hoy)

    # ============================================================
    # 3️⃣ LISTA DE FECHAS DISPONIBLES
    # ============================================================
    cursor.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas_raw = cursor.fetchall()

    if not fechas_raw:
        st.info("Aún no hay reuniones registradas.")
        return

    fechas = [fila["fecha"] for fila in fechas_raw]

    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ============================================================
    # 4️⃣ RESUMEN DEL DÍA SELECCIONADO
    # ============================================================
    cursor.execute("""
        SELECT *
        FROM caja_reunion
        WHERE fecha = %s
    """, (fecha_sel,))
    
    reunion = cursor.fetchone()

    if not reunion:
        st.warning("No se encontró información de caja para esta fecha.")
        return

    id_caja = reunion["id_caja"]
    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])

    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos", f"${ingresos:.2f}")
    col3.metric("Egresos", f"${egresos:.2f}")

    st.metric("💰 Saldo Final del Día", f"${saldo_final:.2f}")

    st.markdown("---")

    # ============================================================
    # 5️⃣ DETALLE DE MOVIMIENTOS DEL DÍA
    # ============================================================
    st.subheader("📋 Movimientos del día")

    cursor.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = %s
        ORDER BY id_mov ASC
    """, (id_caja,))

    movimientos = cursor.fetchall()

    if not movimientos:
        st.info("No hay movimientos registrados en esta reunión.")
    else:
        df_mov = pd.DataFrame(movimientos)
        st.dataframe(df_mov, hide_index=True, use_container_width=True)

    st.markdown("---")

    # ============================================================
    # 6️⃣ RESUMEN DEL CICLO
    # ============================================================
    st.subheader("📊 Resumen general del ciclo")

    cursor.execute("""
        SELECT 
            IFNULL(SUM(CASE WHEN tipo='Ingreso' THEN monto END),0) AS total_ingresos,
            IFNULL(SUM(CASE WHEN tipo='Egreso' THEN monto END),0) AS total_egresos
        FROM caja_movimientos
        WHERE fecha >= %s
    """, (ciclo_inicio,))

    totales = cursor.fetchone()
    total_ingresos = float(totales["total_ingresos"])
    total_egresos = float(totales["total_egresos"])
    balance_ciclo = total_ingresos - total_egresos

    st.write(f"📥 **Ingresos acumulados:** ${total_ingresos:.2f}")
    st.write(f"📤 **Egresos acumulados:** ${total_egresos:.2f}")
    st.success(f"💼 **Balance del ciclo:** ${balance_ciclo:.2f}")

    # ============================================================
    # 7️⃣ GRÁFICA — INGRESOS VS EGRESOS (CICLO)
    # ============================================================
    st.subheader("📈 Gráfica del ciclo")

    fig, ax = plt.subplots()
    ax.bar(["Ingresos", "Egresos"], [total_ingresos, total_egresos])
    ax.set_title("Ingresos vs Egresos del Ciclo")
    ax.set_ylabel("Monto ($)")
    st.pyplot(fig)

    # Pie chart por categorías
    cursor.execute("""
        SELECT categoria, SUM(monto) AS total
        FROM caja_movimientos
        WHERE fecha >= %s
        GROUP BY categoria
    """, (ciclo_inicio,))
        
    categorias = cursor.fetchall()

    if categorias:
        labels = [c["categoria"] for c in categorias]
        values = [c["total"] for c in categorias]

        fig2, ax2 = plt.subplots()
        ax2.pie(values, labels=labels, autopct="%1.1f%%")
        ax2.set_title("Distribución por categoría")
        st.pyplot(fig2)

    st.markdown("---")

    # ============================================================
    # 8️⃣ GENERAR PDF COMPLETO
    # ============================================================
    st.subheader("📄 Exportar reporte a PDF")

    if st.button("📥 Descargar PDF"):

        nombre_pdf = f"reporte_caja_{fecha_sel}.pdf"
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)

        contenido = []

        contenido.append(Paragraph(f"<b>Reporte de Caja — {fecha_sel}</b>", styles["Title"]))
        contenido.append(Spacer(1, 12))

        # Tabla del día
        tabla_dia = [
            ["Campo", "Valor"],
            ["Saldo Inicial", f"${saldo_inicial:.2f}"],
            ["Ingresos", f"${ingresos:.2f}"],
            ["Egresos", f"${egresos:.2f}"],
            ["Saldo Final", f"${saldo_final:.2f}"],
        ]

        t_day = Table(tabla_dia, colWidths=[150, 300])
        t_day.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))

        contenido.append(Paragraph("<b>Resumen del día</b>", styles["Heading2"]))
        contenido.append(t_day)
        contenido.append(Spacer(1, 12))

        # Tabla del ciclo
        tabla_ciclo = [
            ["Campo", "Valor"],
            ["Ingresos acumulados", f"${total_ingresos:.2f}"],
            ["Egresos acumulados", f"${total_egresos:.2f}"],
            ["Balance del ciclo", f"${balance_ciclo:.2f}"],
        ]

        t_cycle = Table(tabla_ciclo, colWidths=[200, 250])
        t_cycle.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))

        contenido.append(Paragraph("<b>Resumen del ciclo</b>", styles["Heading2"]))
        contenido.append(t_cycle)

        doc.build(contenido)

        with open(nombre_pdf, "rb") as f:
            st.download_button(
                label="📄 Descargar PDF",
                data=f,
                file_name=nombre_pdf,
                mime="application/pdf"
            )

    cursor.close()
    con.close()
