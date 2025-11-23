import streamlit as st
from datetime import date
from decimal import Decimal

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_actual


# ------------------------------------------------------------
# PDF – Comprobante de gasto
# ------------------------------------------------------------
def generar_pdf_gasto(fecha, categoria, monto, saldo_antes, saldo_despues):
    nombre_pdf = f"gasto_{fecha}.pdf"
    doc = SimpleDocTemplate(nombre_pdf, pagesize=letter)

    estilos = getSampleStyleSheet()
    contenido = []

    titulo = Paragraph("<b>Comprobante de Gasto</b>", estilos["Title"])
    contenido.append(titulo)

    data = [
        ["Campo", "Detalle"],
        ["Fecha", fecha],
        ["Categoría", categoria],
        ["Monto del gasto", f"${monto:.2f}"],
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
# Pantalla principal – Registrar gastos
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
    # CATEGORÍA DEL GASTO
    # --------------------------------------------------------
    categoria = st.text_input("Categoría del gasto (Ej: Transporte, Materiales, Servicios)").strip()

    # --------------------------------------------------------
    # MONTO DEL GASTO
    # --------------------------------------------------------
    monto_raw = st.number_input(
        "Monto del gasto ($)",
        min_value=0.01,
        format="%.2f",
        step=0.01
    )
    monto = Decimal(str(monto_raw))

    # --------------------------------------------------------
    # OBTENER SALDO REAL (caja_general)
    # --------------------------------------------------------
    saldo_real = obtener_saldo_actual()
    st.info(f"📌 Saldo disponible (caja actual): **${saldo_real:,.2f}**")

    # --------------------------------------------------------
    # VALIDACIÓN
    # --------------------------------------------------------
    if monto > saldo_real:
        st.error(f"❌ No puedes registrar un gasto mayor al saldo disponible (${saldo_real:,.2f}).")
        return

    # --------------------------------------------------------
    # OBTENER O CREAR REUNIÓN (solo para reportes)
    # --------------------------------------------------------
    id_reunion = obtener_o_crear_reunion(fecha)

    # --------------------------------------------------------
    # BOTÓN PARA GUARDAR EL GASTO
    # --------------------------------------------------------
    if st.button("💾 Registrar gasto"):

        try:
            # Registrar movimiento (tipo Egreso)
            registrar_movimiento(
                id_caja=id_reunion,
                tipo="Egreso",
                categoria=categoria,
                monto=monto
            )

            # Obtener nuevo saldo actual
            saldo_despues = obtener_saldo_actual()

            # Generar PDF
            pdf_path = generar_pdf_gasto(
                fecha,
                categoria,
                float(monto),
                float(saldo_real),
                float(saldo_despues)
            )

            st.success("✅ Gasto registrado correctamente.")

            st.download_button(
                "📄 Descargar comprobante PDF",
                data=open(pdf_path, "rb").read(),
                file_name=pdf_path,
                mime="application/pdf"
            )

        except Exception as e:
            st.error("❌ Error al registrar el gasto.")
            st.write(str(e))

    cursor.close()
    con.close()
