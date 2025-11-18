import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from modulos.config.conexion import obtener_conexion

# --------------------------------------------------------------------
#  FUNCIÓN PARA GENERAR EL FORMULARIO DE ASISTENCIA
# --------------------------------------------------------------------

def generar_pdf_asistencia(socias):
    filename = "formulario_asistencia.pdf"
    c = canvas.Canvas(filename, pagesize=letter)

    # Tamaño de página
    width, height = letter

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 40, "FORMULARIO DE ASISTENCIA")

    # Configuración de tabla
    x_start = 20
    y_start = height - 100
    row_height = 18
    col_num = 12  # # | Socia | M/H | 10 fechas
    col_widths = [
        20,   # #
        200,  # Nombre
        25,   # M/H
    ] + [45] * 10  # 10 fechas vacías

    # Encabezados
    headers = ["#", "Socia", "M/H"] + [f"Fecha" for _ in range(10)]

    # Dibujar encabezados
    y = y_start
    x = x_start
    c.setFont("Helvetica-Bold", 8)

    for i, h in enumerate(headers):
        c.rect(x, y, col_widths[i], row_height)
        c.drawCentredString(x + col_widths[i] / 2, y + 5, h)
        x += col_widths[i]

    # Filas con socias
    c.setFont("Helvetica", 8)
    y -= row_height

    for idx, socia in enumerate(socias, start=1):
        x = x_start

        row = [
            str(idx),           # Número
            socia["Nombre"],    # Nombre socia
            " "                 # M/H vacío
        ] + [""] * 10           # 10 fechas vacías

        for i, value in enumerate(row):
            c.rect(x, y, col_widths[i], row_height)

            # Alinear texto
            if i == 1:  # Nombre a la izquierda
                c.drawString(x + 2, y + 4, value)
            else:
                c.drawCentredString(x + col_widths[i] / 2, y + 4, value)

            x += col_widths[i]

        y -= row_height

    c.save()
    return filename


# --------------------------------------------------------------------
#  INTERFAZ STREAMLIT
# --------------------------------------------------------------------

def pagina_asistencia():
    st.title("📋 Registro de asistencia")

    try:
        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre")
        socias = cursor.fetchall()
    except Exception as e:
        st.error(f"Error cargando socias: {e}")
        return

    st.success("Socias cargadas correctamente.")

    if st.button("📄 Generar formulario de asistencia (PDF)"):
        filename = generar_pdf_asistencia(socias)

        with open(filename, "rb") as f:
            st.download_button(
                label="⬇ Descargar formulario",
                data=f,
                file_name=filename,
                mime="application/pdf"
            )
        st.success("Formulario generado correctamente.")
