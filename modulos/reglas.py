import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import datetime


# ============================================================
# PANEL PRINCIPAL
# ============================================================
def gestionar_reglas():

    st.title("📘 Reglas internas del grupo")

    seccion = st.radio(
        "Seleccione una sección:",
        [
            "Editor de reglas internas",
            "Comité directivo",
            "Permisos válidos de inasistencia",
            "Exportar reglas en PDF"
        ]
    )

    if seccion == "Editor de reglas internas":
        editor_reglas()

    elif seccion == "Comité directivo":
        mostrar_comite()

    elif seccion == "Permisos válidos de inasistencia":
        mostrar_permisos()

    elif seccion == "Exportar reglas en PDF":
        exportar_pdf()



# ============================================================
# 1. EDITOR DE REGLAS INTERNAS
# ============================================================
def editor_reglas():

    st.subheader("📖 Editor de reglas internas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo WHERE id_regla = 1")
    datos = cursor.fetchone()

    if not datos:
        st.error("No existe el registro de reglas internas (id_regla = 1).")
        return

    # ------ campos existentes en tu tabla ------
    nombre_grupo = st.text_input("Nombre del Grupo", datos["nombre_grupo"])
    nombre_comunidad = st.text_input("Comunidad", datos["nombre_comunidad"])

    multa_inasistencia = st.number_input(
        "Multa por inasistencia ($)",
        min_value=0.0, step=0.25,
        value=float(datos["multa_inasistencia"])
    )

    ahorro_minimo = st.number_input(
        "Ahorro mínimo ($)",
        min_value=0.0, step=0.25,
        value=float(datos["ahorro_minimo"])
    )

    interes_por_10 = st.number_input(
        "Interés por cada $10 prestados (%)",
        min_value=0.0, step=0.1,
        value=float(datos["interes_por_10"])
    )

    prestamo_maximo = st.number_input(
        "Préstamo máximo ($)",
        min_value=0.0, step=1.0,
        value=float(datos["prestamo_maximo"])
    )

    plazo_maximo = st.number_input(
        "Plazo máximo (meses)",
        min_value=1, step=1,
        value=int(datos["plazo_maximo"])
    )

    otras_reglas = st.text_area("Otras reglas", datos["otras_reglas"])

    # ------------------ GUARDAR ------------------
    if st.button("💾 Guardar cambios"):

        cursor.execute("""
            UPDATE reglas_grupo
            SET nombre_grupo=%s,
                nombre_comunidad=%s,
                multa_inasistencia=%s,
                ahorro_minimo=%s,
                interes_por_10=%s,
                prestamo_maximo=%s,
                plazo_maximo=%s,
                otras_reglas=%s
            WHERE id_regla = 1
        """, (
            nombre_grupo,
            nombre_comunidad,
            multa_inasistencia,
            ahorro_minimo,
            interes_por_10,
            prestamo_maximo,
            plazo_maximo,
            otras_reglas
        ))

        con.commit()
        st.success("Cambios guardados correctamente.")
        st.rerun()


# ============================================================
# 2. COMITÉ DIRECTIVO
# ============================================================
def mostrar_comite():

    st.subheader("👥 Comité directivo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id_comite, c.cargo, s.Nombre AS nombre_socia
        FROM comite_directiva c
        JOIN Socia s ON s.Id_Socia = c.id_regla
        ORDER BY c.id_comite ASC
    """)
    datos = cursor.fetchall()

    if not datos:
        st.info("No hay miembros registrados.")
    else:
        st.table(pd.DataFrame(datos))



# ============================================================
# 3. PERMISOS VÁLIDOS DE INASISTENCIA
# ============================================================
def mostrar_permisos():

    st.subheader("📝 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Agregar un permiso nuevo
    nuevo = st.text_input("Agregar nuevo permiso")

    if st.button("➕ Registrar permiso"):
        if nuevo.strip():
            cursor.execute("""
                INSERT INTO regla_permisos_inasistencia (descripcion)
                VALUES (%s)
            """, (nuevo,))
            con.commit()
            st.success("Permiso registrado.")
            st.rerun()
        else:
            st.warning("Ingrese un texto válido.")

    st.divider()

    cursor.execute("SELECT id_permiso, descripcion FROM regla_permisos_inasistencia")
    permisos = cursor.fetchall()

    if not permisos:
        st.info("No hay permisos registrados.")
        return

    st.subheader("Permisos registrados:")
    for p in permisos:
        col1, col2 = st.columns([5, 1])
        col1.write(p["descripcion"])
        if col2.button("Eliminar", key=f"del{p['id_permiso']}"):
            cursor.execute("DELETE FROM regla_permisos_inasistencia WHERE id_permiso=%s", (p["id_permiso"],))
            con.commit()
            st.rerun()



# ============================================================
# 4. EXPORTAR PDF
# ============================================================
def exportar_pdf():

    st.subheader("📄 Exportar todas las reglas en PDF")

    if st.button("📥 Generar PDF"):

        con = obtener_conexion()
        cursor = con.cursor(dictionary=True)

        cursor.execute("SELECT * FROM reglas_grupo WHERE id_regla = 1")
        datos = cursor.fetchone()

        if not datos:
            st.error("No se encontraron reglas para exportar.")
            return

        filename = "/mnt/data/reglas_internas.pdf"

        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(filename, pagesize=letter)

        contenido = []

        contenido.append(Paragraph("<b>REGLAS INTERNAS DEL GRUPO</b>", styles["Title"]))
        contenido.append(Spacer(1, 18))

        contenido.append(Paragraph(f"<b>Nombre del grupo:</b> {datos['nombre_grupo']}", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Comunidad:</b> {datos['nombre_comunidad']}", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Multa por inasistencia:</b> ${datos['multa_inasistencia']}", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Ahorro mínimo:</b> ${datos['ahorro_minimo']}", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Interés por cada $10 prestados:</b> {datos['interes_por_10']}%", styles["Normal"]))
        contenido.append(Paragraph(f"<b>Préstamo máximo:</b> ${datos['prestamo_maximo']}", styles["Normal"]))
       contenido.append(Paragraph(f"<b>Plazo máximo:</b> {datos['plazo_maximo']} meses", styles["Normal"]))
        contenido.append(Spacer(1, 12))

        contenido.append(Paragraph("<b>Otras reglas:</b>", styles["Heading3"]))
        contenido.append(Paragraph(datos["otras_reglas"], styles["Normal"]))

        contenido.append(Spacer(1, 20))
        contenido.append(Paragraph(f"Fecha de emisión: {datetime.date.today()}", styles["Normal"]))

        doc.build(contenido)

        st.success("PDF generado correctamente.")
        st.download_button("📥 Descargar PDF", data=open(filename, "rb").read(), file_name="reglas_internas.pdf")


