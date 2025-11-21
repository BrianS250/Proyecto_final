import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_saldo_por_fecha
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def cierre_ciclo():

    st.header("🔚 Cierre de Ciclo – Solidaridad CVX")

    # ----------------------------------
    # FECHA DEL CIERRE
    # ----------------------------------
    fecha_raw = st.date_input("📅 Fecha del cierre", date.today())
    fecha_cierre = fecha_raw.strftime("%Y-%m-%d")

    # ----------------------------------
    # RESPONSABLE
    # ----------------------------------
    responsable = st.text_input("👤 Responsable del cierre (Directiva)")
    observaciones = st.text_area("📝 Observaciones del cierre (opcional)")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ----------------------------------
    # OBTENER CICLO ACTUAL
    # ----------------------------------
    cursor.execute("SELECT * FROM ciclo ORDER BY id_ciclo DESC LIMIT 1")
    ciclo_actual = cursor.fetchone()

    if not ciclo_actual:
        st.error("❌ No existe ningún ciclo activo. Debes crear uno antes de cerrar.")
        return

    id_ciclo = ciclo_actual["id_ciclo"]
    fecha_inicio = ciclo_actual["fecha_inicio"]

    # ----------------------------------
    # OBTENER SALDO FINAL A ESA FECHA
    # ----------------------------------
    saldo_final = obtener_saldo_por_fecha(fecha_cierre)

    st.info(f"💰 **Saldo final de caja al {fecha_cierre}: ${saldo_final:.2f}**")

    # ----------------------------------
    # BOTÓN PRINCIPAL
    # ----------------------------------
    if st.button("🔐 Cerrar Ciclo"):

        if responsable.strip() == "":
            st.warning("⚠ Debe escribir un responsable para el cierre.")
            return

        # Guardar cierre en la base de datos
        cursor.execute("""
            INSERT INTO cierre_ciclo (id_ciclo, fecha_cierre, saldo_final, observaciones, responsable)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_ciclo, fecha_cierre, saldo_final, observaciones, responsable))
        con.commit()

        id_cierre = cursor.lastrowid

        # ----------------------------------
        # CREAR AUTOMÁTICAMENTE EL NUEVO CICLO
        # ----------------------------------
        cursor.execute("""
            INSERT INTO ciclo (fecha_inicio, saldo_inicial)
            VALUES (%s, %s)
        """, (fecha_cierre, saldo_final))
        con.commit()

        # ----------------------------------
        # GENERAR PDF
        # ----------------------------------
        nombre_pdf = f"cierre_ciclo_{id_cierre}.pdf"
        styles = getSampleStyleSheet()

        doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
        elementos = []

        # Título
        titulo = Paragraph(
            "<b><font size=16>SOLIDARIDAD CVX</font></b>",
            styles["Title"]
        )
        elementos.append(titulo)
        elementos.append(Spacer(1, 12))

        subtitulo = Paragraph(
            "<b><font size=14>Cierre de Ciclo</font></b>",
            styles["Title"]
        )
        elementos.append(subtitulo)
        elementos.append(Spacer(1, 24))

        tabla = Table([
            ["Campo", "Valor"],
            ["Fecha de inicio del ciclo", str(fecha_inicio)],
            ["Fecha de cierre del ciclo", fecha_cierre],
            ["Saldo final del ciclo", f"${saldo_final:.2f}"],
            ["Responsable", responsable],
            ["Observaciones", observaciones if observaciones else "Ninguna"]
        ])

        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.gray),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("BOX", (0,0), (-1,-1), 1, colors.black),
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ]))

        elementos.append(tabla)
        elementos.append(Spacer(1, 25))

        firma = Paragraph("<b>Firma del responsable:</b> ________________________________", styles["Normal"])
        elementos.append(firma)

        doc.build(elementos)

        # Descargar PDF
        with open(nombre_pdf, "rb") as f:
            st.download_button(
                "📥 Descargar PDF del cierre",
                f,
                file_name=nombre_pdf
            )

        st.success("✔ Ciclo cerrado exitosamente. El nuevo ciclo fue creado automáticamente.")
        st.balloons()
