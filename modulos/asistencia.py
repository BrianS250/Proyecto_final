import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from modulos.config.conexion import obtener_conexion


# ================================
#   INTERFAZ PRINCIPAL DE ASISTENCIA
# ================================
def interfaz_asistencia():
    st.header("📋 Formulario de Asistencia")

    st.write("Generar formulario de asistencia para las reuniones del grupo.")

    # Datos requeridos
    fecha_reunion = st.date_input("Fecha de la reunión")
    modalidad = st.selectbox("Modalidad (M/H):", ["M", "H"])

    st.info("El formulario generará únicamente **10 filas** como solicitaste.")

    if st.button("📄 Generar formulario PDF"):
        generar_pdf_asistencia(str(fecha_reunion), modalidad)
        st.success("Formulario generado correctamente. Descárguelo abajo.")

        with open("formulario_asistencia.pdf", "rb") as f:
            st.download_button(
                "⬇️ Descargar formulario",
                f,
                file_name="formulario_asistencia.pdf"
            )


# ================================
#   FUNCIÓN PARA GENERAR EL PDF
# ================================
def generar_pdf_asistencia(fecha, modalidad):
    archivo = "formulario_asistencia.pdf"
    c = canvas.Canvas(archivo, pagesize=letter)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(180, 760, "FORMULARIO DE ASISTENCIA")

    # Encabezado
    c.setFont("Helvetica", 11)
    c.drawString(50, 735, "Fecha:")
    c.drawString(100, 735, fecha)

    c.drawString(300, 735, "M/H:")
    c.drawString(340, 735, modalidad)

    # Cabecera de tabla
    y = 710
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, y, "#")
    c.drawString(80, y, "Socia")
    c.drawString(250, y, "M/H")

    # 10 columnas de fechas
    x_date = 310
    for i in range(10):
        c.drawString(x_date + i * 50, y, f"Fecha {i + 1}")

    # Filas (solo 10)
    c.setFont("Helvetica", 9)
    y -= 20

    for i in range(1, 11):
        c.drawString(50, y, str(i))         # número
        c.drawString(80, y, "")             # nombre socia
        c.drawString(250, y, modalidad)     # M/H

        # Casillas de asistencia
        for j in range(10):
            c.rect(310 + j*50, y - 5, 40, 17)

        y -= 25

    c.save()
