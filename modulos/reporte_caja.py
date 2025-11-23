import streamlit as st
import pandas as pd
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 📊 REPORTE DE CAJA — CORREGIDO Y COHERENTE
# ============================================================
def reporte_caja():

    st.title("📊 Reporte de Caja — Sistema Solidaridad CVX")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ LEER FECHA DE INICIO DEL CICLO
    # ============================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ Debes registrar las reglas internas primero.")
        return

    ciclo_inicio = reglas.get("ciclo_inicio")
    if not ciclo_inicio:
        st.error("⚠ Falta la fecha de inicio del ciclo en reglas internas.")
        return

    # ============================================================
    # 2️⃣ CREAR REUNIÓN HOY SI NO EXISTE
    # ============================================================
    hoy = date.today().strftime("%Y-%m-%d")
    obtener_o_crear_reunion(hoy)

    # ============================================================
    # 3️⃣ LISTA DE FECHAS CON MOVIMIENTOS
    # ============================================================
    cur.execute("SELECT fecha FROM caja_reunion ORDER BY fecha DESC")
    fechas_raw = cur.fetchall()

    if not fechas_raw:
        st.info("Aún no hay reuniones registradas.")
        return

    fechas = [f["fecha"] for f in fechas_raw]
    fecha_sel = st.selectbox("📅 Seleccione la fecha:", fechas)

    # ============================================================
    # 4️⃣ CARGAR REUNIÓN
    # ============================================================
    cur.execute("SELECT * FROM caja_reunion WHERE fecha = %s", (fecha_sel,))
    reunion = cur.fetchone()

    if not reunion:
        st.warning("No existe información de caja para esta fecha.")
        return

    id_caja = reunion["id_caja"]

    # ============================================================
    # 5️⃣ CALCULAR SALDO INICIAL REAL
    # ============================================================
    # Si existen días anteriores, saldo_inicial = saldo_final del día anterior
    cur.execute("""
        SELECT saldo_final 
        FROM caja_reunion 
        WHERE fecha < %s 
        ORDER BY fecha DESC 
        LIMIT 1
    """, (fecha_sel,))
    dia_anterior = cur.fetchone()

    if dia_anterior:
        saldo_inicial = float(dia_anterior["saldo_final"])
    else:
        saldo_inicial = float(reunion["saldo_inicial"])  # si es el primer día del ciclo

    # ============================================================
    # 6️⃣ CALCULAR INGRESOS Y EGRESOS DEL DÍA (REAL)
    # ============================================================
    cur.execute("""
        SELECT 
            IFNULL(SUM(CASE WHEN tipo='Ingreso' THEN monto END), 0) AS ingresos,
            IFNULL(SUM(CASE WHEN tipo='Egreso' THEN monto END), 0) AS egresos
        FROM caja_movimientos cm
        JOIN caja_reunion cr ON cr.id_caja = cm.id_caja
        WHERE cr.fecha = %s
    """, (fecha_sel,))

    totales_dia = cur.fetchone()
    ingresos = float(totales_dia["ingresos"])
    egresos = float(totales_dia["egresos"])

    # ============================================================
    # 7️⃣ SALDO FINAL DEL DÍA (COHERENTE CON LA CAJA REAL)
    # ============================================================
    if fecha_sel == hoy:
        # hoy siempre debe coincidir con caja_actual
        cur.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
        saldo_actual = cur.fetchone()
        saldo_final = float(saldo_actual["saldo_actual"])
    else:
        # días anteriores se calculan matemáticamente
        saldo_final = saldo_inicial + ingresos - egresos

    # ============================================================
    # 8️⃣ MOSTRAR RESUMEN
    # ============================================================
    st.subheader(f"📘 Resumen del día — {fecha_sel}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Saldo Inicial", f"${saldo_inicial:.2f}")
    col2.metric("Ingresos", f"${ingresos:.2f}")
    col3.metric("Egresos", f"${egresos:.2f}")

    st.metric("💰 Saldo Final del Día", f"${saldo_final:.2f}")

    st.markdown("---")

    # ============================================================
    # 9️⃣ MOVIMIENTOS DEL DÍA
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
        df = pd.DataFrame(movimientos)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.info("No hay movimientos registrados en esta fecha.")

    st.markdown("---")

    # ============================================================
    # 🔟 RESUMEN DEL CICLO
    # ============================================================
    st.subheader("📊 Resumen general del ciclo")

    cur.execute("""
        SELECT 
            IFNULL(SUM(CASE WHEN tipo='Ingreso' THEN monto END), 0) AS total_ingresos,
            IFNULL(SUM(CASE WHEN tipo='Egreso' THEN monto END), 0) AS total_egresos
        FROM caja_movimientos M
        JOIN caja_reunion R ON R.id_caja = M.id_caja
        WHERE R.fecha >= %s
    """, (ciclo_inicio,))

    ciclo = cur.fetchone()
    total_ingresos = float(ciclo["total_ingresos"])
    total_egresos = float(ciclo["total_egresos"])
    balance_ciclo = total_ingresos - total_egresos

    st.write(f"📥 **Ingresos acumulados:** ${total_ingresos:.2f}")
    st.write(f"📤 **Egresos acumulados:** ${total_egresos:.2f}")
    st.success(f"💼 **Balance del ciclo:** ${balance_ciclo:.2f}")

    st.markdown("---")

    # ============================================================
    # 1️⃣1️⃣ EXPORTAR PDF (sin cambios)
    # ============================================================
    if st.button("📄 Descargar PDF"):

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
        ]

        t_day = Table(tabla_dia)
        t_day.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))

        contenido.append(t_day)
        contenido.append(Spacer(1, 12))

        tabla_ciclo = [
            ["Campo", "Valor"],
            ["Ingresos acumulados", f"${total_ingresos:.2f}"],
            ["Egresos acumulados", f"${total_egresos:.2f}"],
            ["Balance del ciclo", f"${balance_ciclo:.2f}"],
        ]

        t_cycle = Table(tabla_ciclo)
        t_cycle.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))

        contenido.append(t_cycle)

        doc.build(contenido)

        with open(nombre_pdf, "rb") as f:
            st.download_button(
                label="📥 Descargar PDF",
                data=f,
                file_name=nombre_pdf,
                mime="application/pdf"
            )

    cur.close()
    con.close()
