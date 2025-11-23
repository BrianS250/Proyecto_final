import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal
import os

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, obtener_saldo_actual
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📊 REPORTE DE CAJA COMPLETO — SIN MATPLOTLIB
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ CICLO – REGLAS INTERNAS
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
    fechas = [f["fecha"] for f in cur.fetchall()]

    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ============================================================
    # 3️⃣ RESUMEN DEL DÍA
    # ============================================================
    cur.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha_sel,))
    reunion = cur.fetchone()

    id_caja = reunion["id_caja"]
    saldo_inicial = float(reunion["saldo_inicial"])
    ingresos = float(reunion["ingresos"])
    egresos = float(reunion["egresos"])
    saldo_final = float(reunion["saldo_final"])
    dia_cerrado = reunion["dia_cerrado"]

    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    c1, c2, c3 = st.columns(3)
    c1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    c2.metric("Ingresos", f"${ingresos:.2f}")
    c3.metric("Egresos", f"${egresos:.2f}")
    st.metric("💰 Saldo Final", f"${saldo_final:.2f}")

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
    # 5️⃣ CIERRE DE DÍA
    # ============================================================
    st.subheader("🧾 Cierre del día")

    if dia_cerrado == 1:
        st.success("🔒 Este día ya está cerrado.")
    else:
        st.warning("⚠ Este día NO está cerrado aún.")

        if st.button("✅ Cerrar este día definitivamente"):

            saldo_real = float(obtener_saldo_actual())
            saldo_calc = saldo_inicial + ingresos - egresos

            if abs(saldo_real - saldo_calc) > 0.01:
                st.error(
                    f"❌ No se puede cerrar el día.\n\n"
                    f"Saldo calculado: ${saldo_calc:.2f}\n"
                    f"Saldo real: ${saldo_real:.2f}\n"
                    "Los valores no coinciden."
                )
                return

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
            IFNULL(SUM(CASE WHEN tipo='Ingreso' THEN monto END),0) AS total_ingresos,
            IFNULL(SUM(CASE WHEN tipo='Egreso' THEN monto END),0) AS total_egresos
        FROM caja_movimientos cm
        JOIN caja_reunion cr ON cr.id_caja = cm.id_caja
        WHERE cr.fecha >= %s
    """, (ciclo_inicio,))
    tot = cur.fetchone()

    total_ingresos = float(tot["total_ingresos"])
    total_egresos = float(tot["total_egresos"])
    balance = total_ingresos - total_egresos

    st.write(f"📥 Ingresos acumulados: **${total_ingresos:.2f}**")
    st.write(f"📤 Egresos acumulados: **${total_egresos:.2f}**")
    st.success(f"💼 Balance del ciclo: **${balance:.2f}**")

    st.markdown("---")

    # ============================================================
    # 7️⃣ GRAFICAS NATIVAS — AL FINAL
    # ============================================================
    st.subheader("📈 Gráficas del día")

    # --- Construir dataframe del día ---
    df_dia = pd.DataFrame(movimientos)
    df_dia["monto"] = df_dia["monto"].astype(float)

    # INGRESOS
    df_ing = df_dia[df_dia["tipo"] == "Ingreso"]
    st.write("### 📈 Ingresos del día")
    if not df_ing.empty:
        st.line_chart(df_ing[["monto"]])
    else:
        st.info("No hubo ingresos ese día.")

    # EGRESOS
    df_egr = df_dia[df_dia["tipo"] == "Egreso"]
    st.write("### 📉 Egresos del día")
    if not df_egr.empty:
        st.line_chart(df_egr[["monto"]])
    else:
        st.info("No hubo egresos ese día.")

    # Comparativa del día
    st.write("### 📊 Comparación del día")
    st.bar_chart(pd.DataFrame({
        "Ingresos": [ingresos],
        "Egresos": [egresos],
        "Saldo Final": [saldo_final]
    }))

    st.markdown("---")

    # ============================================================
    # 8️⃣ PDF SOLO RESUMEN DEL DÍA — SIN GRAFICAS
    # ============================================================
    st.subheader("📄 Exportar resumen del día a PDF")

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

        contenido.append(t_day)

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
