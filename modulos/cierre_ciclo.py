import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

# PDF / HTML
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import io
import base64


# ---------------------------------------------------------
# OBTENER CICLO ACTIVO
# ---------------------------------------------------------
def obtener_ciclo_activo():
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT * FROM ciclo_resumen
        WHERE fecha_cierre IS NULL
        ORDER BY id_ciclo_resumen DESC
        LIMIT 1
    """)
    ciclo = cur.fetchone()
    con.close()
    return ciclo


# ---------------------------------------------------------
# VALIDAR PRÉSTAMOS PENDIENTES
# ---------------------------------------------------------
def prestamos_pendientes():
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT Id_Préstamo, `Saldo pendiente`, Id_Socia
        FROM Prestamo
        WHERE `Saldo pendiente` > 0
    """)

    pendientes = cur.fetchall()
    con.close()
    return pendientes


# ---------------------------------------------------------
# OBTENER SALDO INICIAL
# ---------------------------------------------------------
def obtener_saldo_inicial(fecha_inicio):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_inicial 
        FROM caja_reunion
        WHERE fecha >= %s
        ORDER BY fecha ASC
        LIMIT 1
    """, (fecha_inicio,))
    fila = cur.fetchone()

    con.close()
    return fila[0] if fila else 0


# ---------------------------------------------------------
# OBTENER SALDO FINAL
# ---------------------------------------------------------
def obtener_saldo_final(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT saldo_final
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (fecha_inicio, fecha_fin))

    fila = cur.fetchone()
    con.close()
    return fila[0] if fila else 0


# ---------------------------------------------------------
# OBTENER TOTALES DEL CICLO
# ---------------------------------------------------------
def obtener_totales(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    # INGRESOS
    cur.execute("""
        SELECT COALESCE(SUM(ingresos), 0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    ingresos = cur.fetchone()[0]

    # EGRESOS
    cur.execute("""
        SELECT COALESCE(SUM(egresos), 0)
        FROM caja_reunion
        WHERE fecha BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    egresos = cur.fetchone()[0]

    con.close()
    return ingresos, egresos


# ---------------------------------------------------------
# AHORROS POR SOCIA
# ---------------------------------------------------------
def obtener_ahorros_por_socia(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("""
        SELECT S.Id_Socia, S.Nombre AS nombre,
               COALESCE(SUM(A.`Monto del aporte`), 0) AS ahorro_total
        FROM Socia S
        LEFT JOIN Ahorro A ON A.Id_Socia = S.Id_Socia
            AND A.`Fecha del aporte` BETWEEN %s AND %s
        GROUP BY S.Id_Socia, S.Nombre
        ORDER BY S.Id_Socia
    """, (fecha_inicio, fecha_fin))

    socias = cur.fetchall()
    con.close()
    return socias


# ---------------------------------------------------------
# CALCULAR UTILIDAD (INTERESES + MULTAS)
# ---------------------------------------------------------
def calcular_utilidad(fecha_inicio, fecha_fin):
    con = obtener_conexion()
    cur = con.cursor()

    cur.execute("""
        SELECT COALESCE(SUM(Monto), 0)
        FROM Multa
        WHERE Fecha_aplicacion BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    multas = cur.fetchone()[0]

    cur.execute("""
        SELECT COALESCE(SUM(Interes_total), 0)
        FROM Prestamo
        WHERE `Fecha del préstamo` BETWEEN %s AND %s
    """, (fecha_inicio, fecha_fin))
    intereses = cur.fetchone()[0]

    con.close()
    return intereses + multas, intereses, multas


# ---------------------------------------------------------
# TABLA PROPORCIONAL
# ---------------------------------------------------------
def generar_tabla_distribucion(socias, utilidad_total):
    total_ahorros = sum(s["ahorro_total"] for s in socias)
    tabla = []

    for s in socias:
        porcentaje = (s["ahorro_total"] / total_ahorros) if total_ahorros > 0 else 0
        porcion = round(porcentaje * utilidad_total, 2)
        monto_final = round(s["ahorro_total"] + porcion, 2)

        tabla.append({
            "id": s["Id_Socia"],
            "nombre": s["nombre"],
            "ahorro": s["ahorro_total"],
            "porcentaje": round(porcentaje * 100, 2),
            "porcion": porcion,
            "monto_final": monto_final
        })

    return tabla


# ---------------------------------------------------------
# HTML DEL ACTA
# ---------------------------------------------------------
def generar_html_acta(fecha_inicio, fecha_fin, saldo_inicial, saldo_final,
                      ingresos, egresos, utilidad_total, intereses, multas,
                      tabla_distribucion):

    total_ahorros = sum(f["ahorro"] for f in tabla_distribucion)

    html = f"""
    <h2>ACTA DE CIERRE DE CICLO – SOLIDARIDAD CVX</h2>
    <hr>
    <h3>1. Información General</h3>
    <p><b>Fecha de inicio:</b> {fecha_inicio}</p>
    <p><b>Fecha de cierre:</b> {fecha_fin}</p>
    <p><b>Saldo inicial:</b> ${saldo_inicial:,.2f}</p>
    <p><b>Saldo final:</b> ${saldo_final:,.2f}</p>
    <p><b>Total ingresos:</b> ${ingresos:,.2f}</p>
    <p><b>Total egresos:</b> ${egresos:,.2f}</p>
    <p><b>Total ahorro del grupo:</b> ${total_ahorros:,.2f}</p>

    <h3>2. Utilidad del ciclo</h3>
    <p><b>Total intereses:</b> ${intereses:,.2f}</p>
    <p><b>Total multas:</b> ${multas:,.2f}</p>
    <p><b>Utilidad total:</b> ${utilidad_total:,.2f}</p>

    <h3>3. Distribución proporcional</h3>
    <table border='1' cellspacing='0' cellpadding='5'>
        <tr>
            <th>#</th>
            <th>Nombre</th>
            <th>Ahorro</th>
            <th>%</th>
            <th>Porción</th>
            <th>Monto final</th>
        </tr>
    """

    for fila in tabla_distribucion:
        html += f"""
        <tr>
            <td>{fila['id']}</td>
            <td>{fila['nombre']}</td>
            <td>${fila['ahorro']:,.2f}</td>
            <td>{fila['porcentaje']}%</td>
            <td>${fila['porcion']:,.2f}</td>
            <td>${fila['monto_final']:,.2f}</td>
        </tr>
        """

    html += """
    </table>

    <br><br>
    <h3>Firmas</h3>
    <p>Presidenta: _______________________</p>
    <p>Secretaria: ________________________</p>
    <p>Tesorera: __________________________</p>
    """

    return html


# ---------------------------------------------------------
# GENERAR PDF
# ---------------------------------------------------------
def generar_pdf_acta(html_content):
    buffer = io.BytesIO()
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    story = []
    story.append(Paragraph(html_content, styles["Normal"]))

    doc.build(story)

    pdf_value = buffer.getvalue()
    buffer.close()
    return pdf_value


# ---------------------------------------------------------
# INTERFAZ PRINCIPAL
# ---------------------------------------------------------
def cierre_ciclo():
    st.title("🔒 Cierre de Ciclo — Solidaridad CVX")

    ciclo = obtener_ciclo_activo()
    if ciclo is None:
        st.warning("❌ No existe ningún ciclo activo.")
        return

    fecha_inicio = ciclo["fecha_inicio"]
    fecha_fin = date.today().strftime("%Y-%m-%d")

    # VALIDAR PRÉSTAMOS PENDIENTES
    pendientes = prestamos_pendientes()

    if pendientes:
        st.error("❌ NO puedes cerrar el ciclo. Hay préstamos pendientes:")
        for p in pendientes:
            st.write(f"- Préstamo #{p['Id_Préstamo']} — Saldo pendiente: ${p['Saldo pendiente']}")
        return

    ingresos, egresos = obtener_totales(fecha_inicio, fecha_fin)
    saldo_inicial = obtener_saldo_inicial(fecha_inicio)
    saldo_final = obtener_saldo_final(fecha_inicio, fecha_fin)

    utilidad_total, intereses, multas = calcular_utilidad(fecha_inicio, fecha_fin)
    socias = obtener_ahorros_por_socia(fecha_inicio, fecha_fin)
    tabla = generar_tabla_distribucion(socias, utilidad_total)

    # RESUMEN
    st.subheader("📘 Resumen del ciclo:")

    st.write(f"**Saldo inicial:** ${saldo_inicial:,.2f}")
    st.write(f"**Saldo final:** ${saldo_final:,.2f}")
    st.write(f"**Ingresos:** ${ingresos:,.2f}")
    st.write(f"**Egresos:** ${egresos:,.2f}")
    st.write(f"**Intereses:** ${intereses:,.2f}")
    st.write(f"**Multas:** ${multas:,.2f}")
    st.write(f"**Utilidad total:** ${utilidad_total:,.2f}")

    st.warning("🟠 Verifica la información antes de cerrar el ciclo.")

    # CERRAR CICLO
    if st.button("🔐 Cerrar ciclo ahora"):
        con = obtener_conexion()
        cur = con.cursor()

        cur.execute("""
            UPDATE ciclo_resumen
            SET fecha_cierre=%s,
                saldo_inicial=%s,
                saldo_final=%s,
                total_ingresos=%s,
                total_egresos=%s,
                total_prestamos_otorgados=0,
                total_prestamos_pagados=0,
                total_multa=%s,
                total_ahorro=0
            WHERE id_ciclo_resumen=%s
        """, (
            fecha_fin,
            saldo_inicial,
            saldo_final,
            ingresos,
            egresos,
            multas,
            ciclo["id_ciclo_resumen"]
        ))

        con.commit()
        con.close()

        st.success("✅ Ciclo cerrado correctamente.")
        st.balloons()

    st.subheader("📄 Acta de Cierre")

    # HTML
    if st.button("📘 Generar Acta HTML"):
        html = generar_html_acta(
            fecha_inicio, fecha_fin,
            saldo_inicial, saldo_final,
            ingresos, egresos,
            utilidad_total, intereses, multas,
            tabla
        )
        st.markdown(html, unsafe_allow_html=True)

    # PDF
    if st.button("⬇️ Descargar Acta PDF"):
        html = generar_html_acta(
            fecha_inicio, fecha_fin,
            saldo_inicial, saldo_final,
            ingresos, egresos,
            utilidad_total, intereses, multas,
            tabla
        )
        pdf = generar_pdf_acta(html)
        b64 = base64.b64encode(pdf).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="Acta_de_Cierre_CVX.pdf">📥 Descargar PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
