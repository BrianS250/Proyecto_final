import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, obtener_saldo_actual
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📊 REPORTE DE CAJA COMPLETO + CIERRE DE DÍA
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ CICLO DESDE REGLAS
    # ============================================================
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ Debes registrar las reglas internas primero.")
        return

    ciclo_inicio = reglas.get("ciclo_inicio")
    if not ciclo_inicio:
        st.error("⚠ Falta la fecha de inicio del ciclo en reglas internas.")
        return

    hoy = date.today().strftime("%Y-%m-%d")
    obtener_o_crear_reunion(hoy)

    # ============================================================
    # 2️⃣ LISTA DE FECHAS DISPONIBLES
    # ============================================================
    cur.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas_raw = cur.fetchall()

    if not fechas_raw:
        st.info("Aún no hay reuniones registradas.")
        return

    fechas = [f["fecha"] for f in fechas_raw]
    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ============================================================
    # 3️⃣ LEER RESUMEN DEL DÍA
    # ============================================================
    cur.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha_sel,))
    reunion = cur.fetchone()

    if not reunion:
        st.warning("No existe información de caja para esta fecha.")
        return

    id_caja = reunion["id_caja"]
    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])
    dia_cerrado = reunion.get("dia_cerrado", 0)

    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos", f"${ingresos:.2f}")
    col3.metric("Egresos", f"${egresos:.2f}")

    st.metric("💰 Saldo Final del Día", f"${saldo_final:.2f}")

    st.markdown("---")

    # ============================================================
    # 4️⃣ MOVIMIENTOS DEL DÍA
    # ============================================================
    st.subheader("📋 Movimientos del día")

    cur.execute("""
        SELECT tipo, categoria, monto
        FROM caja_movimientos
        WHERE id_caja = %s
        ORDER BY id_mov ASC
    """, (id_caja,))
    movimientos = cur.fetchall()

    if movimientos:
        df_mov = pd.DataFrame(movimientos)
        st.dataframe(df_mov, hide_index=True, use_container_width=True)
    else:
        st.info("No hay movimientos registrados en esta reunión.")

    st.markdown("---")

    # ============================================================
    # 5️⃣ CIERRE DE DÍA (si no está cerrado)
    # ============================================================
    st.subheader("🧾 Cierre del día")

    if dia_cerrado == 1:
        st.success("🔒 Este día ya está CERRADO. No se puede modificar.")
    else:
        st.warning("⚠ Este día NO está cerrado todavía.")

        if st.button("✅ Cerrar este día definitivamente"):

            # leer saldo real actual
            saldo_real = float(obtener_saldo_actual())

            # verificar coherencia
            saldo_calculado = saldo_inicial + ingresos - egresos

            if abs(saldo_calculado - saldo_real) > 0.01:
                st.error(
                    f"❌ No se puede cerrar el día.\n\n"
                    f"Saldo calculado: ${saldo_calculado:.2f}\n"
                    f"Saldo real: ${saldo_real:.2f}\n"
                    "Los valores no coinciden."
                )
                return

            # marcar cierre
            cur.execute("""
                UPDATE caja_reunion
                SET dia_cerrado = 1, saldo_final = %s
                WHERE id_caja = %s
            """, (saldo_real, id_caja))
            con.commit()

            st.success("🔒 Día cerrado correctamente.")
            st.experimental_rerun()

    st.markdown("---")

    # ============================================================
    # 6️⃣ RESUMEN DEL CICLO
    # ============================================================
    st.subheader("📊 Resumen general del ciclo")

    cur.execute("""
        SELECT 
            IFNULL(SUM(CASE WHEN M.tipo = 'Ingreso' THEN M.monto END), 0) AS total_ingresos,
            IFNULL(SUM(CASE WHEN M.tipo = 'Egreso' THEN M.monto END), 0) AS total_egresos
        FROM caja_movimientos M
        JOIN caja_reunion R ON R.id_caja = M.id_caja
        WHERE R.fecha >= %s
    """, (ciclo_inicio,))
    totales = cur.fetchone()

    total_ingresos = float(totales["total_ingresos"])
    total_egresos = float(totales["total_egresos"])
    balance_ciclo = total_ingresos - total_egresos

    st.write(f"📥 **Ingresos acumulados:** ${total_ingresos:.2f}")
    st.write(f"📤 **Egresos acumulados:** ${total_egresos:.2f}")
    st.success(f"💼 **Balance del ciclo:** ${balance_ciclo:.2f}")

    st.markdown("---")

    # ============================================================
    # 7️⃣ GENERAR PDF DEL REPORTE
    # ============================================================
    st.subheader("📄 Exportar reporte a PDF")

    if st.button("📥 Descargar PDF"):

        nombre_pdf = f"reporte_caja_{fecha_sel}.pdf"
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        contenido = []

        contenido.append(Paragraph(f"<b>Reporte de Caja — {fecha_sel}</b>", styles["Title"]))
        contenido.append(Spacer(1, 12))

        tabla_dia = [
            ["Campo", "Valor"],
            ["Saldo Inicial", f"${saldo_inicial:.2f}"],
            ["Ingresos", f"${ingresos:.2f}"],
            ["Egresos", f"${egresos:.2f}"],
            ["Saldo Final", f"${saldo_final:.2f}"],
            ["Día Cerrado", "Sí" if dia_cerrado else "No"],
        ]

        t_day = Table(tabla_dia)
        t_day.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))

        contenido.append(Paragraph("<b>Resumen del día</b>", styles["Heading2"]))
        contenido.append(t_day)
        contenido.append(Spacer(1, 12))

        doc.build(contenido)

        with open(nombre_pdf, "rb") as f:
            st.download_button(
                label="📄 Descargar PDF",
                data=f,
                file_name=nombre_pdf,
                mime="application/pdf"
            )

    cur.close()
    con.close()
