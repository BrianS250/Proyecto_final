import streamlit as st
from datetime import date
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ------------------------------------------------------------
# PDF – Generación del comprobante de gasto
# ------------------------------------------------------------
def generar_pdf_gasto(fecha, responsable, descripcion, monto, saldo_antes, saldo_despues):
    nombre_pdf = f"gasto_{fecha}.pdf"

    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)
    estilos = getSampleStyleSheet()
    contenido = []

    titulo = Paragraph("<b>Comprobante de Gasto</b>", estilos["Title"])
    contenido.append(titulo)

    data = [
        ["Campo", "Detalle"],
        ["Fecha", fecha],
        ["Responsable", responsable],
        ["Descripción", descripcion],
        ["Monto", f"${monto:.2f}"],
        ["Saldo antes del gasto", f"${saldo_antes:.2f}"],
        ["Saldo después del gasto", f"${saldo_despues:.2f}"],
    ]

    tabla = Table(data, colWidths=[180, 300])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    contenido.append(tabla)
    doc.build(contenido)

    return nombre_pdf


# ------------------------------------------------------------
# Módulo principal – Registrar gastos
# ------------------------------------------------------------
def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # --------------------------------------------------------
    # FECHA DEL GASTO
    # --------------------------------------------------------
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # RESPONSABLE
    # --------------------------------------------------------
    responsable = st.text_input("Nombre de la persona responsable del gasto").strip()

    # --------------------------------------------------------
    # DESCRIPCIÓN
    # --------------------------------------------------------
    descripcion = st.text_input("Descripción del gasto").strip()

    # --------------------------------------------------------
    # MONTO
    # --------------------------------------------------------
    monto_raw = st.number_input(
        "Monto del gasto ($)",
        min_value=0.01,
        format="%.2f",
        step=0.01
    )
    monto = Decimal(str(monto_raw))

    # --------------------------------------------------------
    # SALDO GLOBAL ACUMULADO (saldo real)
    # --------------------------------------------------------
    cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
    fila_saldo = cursor.fetchone()
    saldo_global = float(fila_saldo["saldo_final"]) if fila_saldo else 0.0

    st.info(f"📌 Saldo disponible (caja actual): **${saldo_global:,.2f}**")

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------
    if monto > saldo_global:
        st.error(
            f"❌ No puedes registrar un gasto mayor al saldo disponible (${saldo_global:,.2f})."
        )
        return

    # --------------------------------------------------------
    # ID DE REUNIÓN (solo para reportes)
    # --------------------------------------------------------
    id_reunion = obtener_o_crear_reunion(fecha)

    # --------------------------------------------------------
    # BOTÓN PARA GUARDAR
    # --------------------------------------------------------
    if st.button("💾 Registrar gasto"):

        try:
            registrar_movimiento(
                id_caja=id_reunion,
                tipo="egreso",
                monto=monto,
                descripcion=descripcion,
                responsable=responsable,
                fecha=fecha
            )

            # Nuevo saldo después del gasto
            cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
            fila_nueva = cursor.fetchone()
            saldo_despues = float(fila_nueva["saldo_final"]) if fila_nueva else saldo_global - float(monto)

            # Generar PDF
            pdf_path = generar_pdf_gasto(
                fecha, responsable, descripcion,
                float(monto), saldo_global, saldo_despues
            )

            st.success("✅ Gasto registrado correctamente.")

            # --------------------------------------------------------
            # 🔥 MEJORA EXIGIDA — Actualizar saldo inmediatamente
            # --------------------------------------------------------
            st.session_state["pdf_gasto"] = pdf_path
            st.session_state["trigger_download"] = True

            st.rerun()

        except Exception as e:
            st.error("❌ Ocurrió un error al registrar el gasto.")
            st.write(e)

    # --------------------------------------------------------
    # 🔥 Mostrar el PDF después del rerun
    # --------------------------------------------------------
    if "trigger_download" in st.session_state and st.session_state["trigger_download"]:
        pdf_path = st.session_state["pdf_gasto"]

        st.download_button(
            "📄 Descargar comprobante PDF",
            data=open(pdf_path, "rb").read(),
            file_name=pdf_path,
            mime="application/pdf"
        )

        # Evitar mostrarlo otra vez
        st.session_state["trigger_download"] = False

    cursor.close()
    con.close()
