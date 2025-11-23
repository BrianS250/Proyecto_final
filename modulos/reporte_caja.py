import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal
import matplotlib.pyplot as plt
import os

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, obtener_saldo_actual
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📊 REPORTE DE CAJA COMPLETO + GRAFICAS + PDF
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

    if not reunion:
        st.warning("No existe información de caja para esta fecha.")
        return

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
        st.dataframe(pd.DataFrame(movimientos), hide_index=True, use_container_width=True)
    else:
        st.info("No hay movimientos registrados en esta reunión.")

    st.markdown("---")

    # ============================================================
    # 5️⃣ CIERRE DE DÍA
    # ============================================================
    st.subheader("🧾 Cierre del día")

    if dia_cerrado == 1:
        st.success("🔒 Este día ya está CERRADO.")
    else:
        st.warning("⚠ Este día NO está cerrado.")

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
    # 7️⃣ GRAFICAS (3) + EXPORTACIÓN PARA EL PDF
    # ============================================================
    st.subheader("📈 Gráficas del ciclo")

    # --- Obtener datos por fecha ---
    cur.execute("""
        SELECT fecha,
               SUM(CASE WHEN tipo='Ingreso' THEN monto END) AS ing,
               SUM(CASE WHEN tipo='Egreso' THEN monto END) AS egr
        FROM caja_movimientos cm
        JOIN caja_reunion cr ON cm.id_caja = cr.id_caja
        WHERE cr.fecha >= %s
        GROUP BY fecha
        ORDER BY fecha ASC
    """, (ciclo_inicio,))
    rows = cur.fetchall()

    df = pd.DataFrame(rows)
    df["ing"] = df["ing"].fillna(0)
    df["egr"] = df["egr"].fillna(0)
    df["saldo"] = df["ing"].cumsum() - df["egr"].cumsum()

    # -------------- Gráfica 1: saldo acumulado --------------
    fig1, ax1 = plt.subplots()
    ax1.plot(df["fecha"], df["saldo"], marker="o")
    ax1.set_title("Saldo acumulado del ciclo")
    ax1.set_xlabel("Fecha")
    ax1.set_ylabel("Saldo ($)")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    g1_path = "/tmp/grafica1.png"
    fig1.savefig(g1_path, dpi=150, bbox_inches="tight")

    # -------------- Gráfica 2: ingresos vs egresos --------------
    fig2, ax2 = plt.subplots()
    ax2.plot(df["fecha"], df["ing"], label="Ingresos", color="green", marker="o")
    ax2.plot(df["fecha"], df["egr"], label="Egresos", color="red", marker="o")
    ax2.set_title("Ingresos vs Egresos (ciclo)")
    plt.xticks(rotation=45)
    ax2.legend()
    st.pyplot(fig2)

    g2_path = "/tmp/grafica2.png"
    fig2.savefig(g2_path, dpi=150, bbox_inches="tight")

    # -------------- Gráfica 3: resumen del día en barras --------------
    fig3, ax3 = plt.subplots()
    ax3.bar(["Ingresos", "Egresos", "Saldo Final"],
            [ingresos, egresos, saldo_final],
            color=["green", "red", "blue"])
    ax3.set_title(f"Resumen del día {fecha_sel}")
    st.pyplot(fig3)

    g3_path = "/tmp/grafica3.png"
    fig3.savefig(g3_path, dpi=150, bbox_inches="tight")

    st.markdown("---")

    # ============================================================
    # 8️⃣ GENERAR PDF
    # ============================================================
    st.subheader("📄 Exportar reporte a PDF completo")

    if st.button("📥 Descargar PDF"):

        nombre_pdf = f"reporte_caja_{fecha_sel}.pdf"
        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        contenido = []

        contenido.append(Paragraph(f"<b>Reporte de Caja — {fecha_sel}</b>", styles["Title"]))
        contenido.append(Spacer(1, 12))

        # --- Tabla resumen ---
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
        contenido.append(Spacer(1, 20))

        # --- Inserción de las 3 gráficas ---
        contenido.append(Paragraph("<b>Gráfica 1 — Saldo acumulado</b>", styles["Heading2"]))
        contenido.append(Image(g1_path, width=480, height=250))
        contenido.append(Spacer(1, 20))

        contenido.append(Paragraph("<b>Gráfica 2 — Ingresos vs Egresos</b>", styles["Heading2"]))
        contenido.append(Image(g2_path, width=480, height=250))
        contenido.append(Spacer(1, 20))

        contenido.append(Paragraph("<b>Gráfica 3 — Resumen del día</b>", styles["Heading2"]))
        contenido.append(Image(g3_path, width=480, height=250))

        doc.build(contenido)

        with open(nombre_pdf, "rb") as f:
            st.download_button(
                label="📄 Descargar PDF completo",
                data=f,
                file_name=nombre_pdf,
                mime="application/pdf"
            )

    cur.close()
    con.close()
