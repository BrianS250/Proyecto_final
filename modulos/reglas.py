import streamlit as st
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from modulos.conexion import obtener_conexion


# ============================================================
# PANEL PRINCIPAL
# ============================================================
def gestionar_reglas():

    st.title("📘 Reglamento Interno del Grupo")

    menu = st.radio(
        "Seleccione una sección:",
        [
            "Editor del Reglamento",
            "Comité Directivo",
            "Exportar Reglamento en PDF"
        ]
    )

    if menu == "Editor del Reglamento":
        editor_reglamento()

    elif menu == "Comité Directivo":
        panel_comite()

    elif menu == "Exportar Reglamento en PDF":
        exportar_pdf()


# ============================================================
# 1. EDITOR COMPLETO DEL REGLAMENTO
# ============================================================
def editor_reglamento():

    st.header("📘 Editor del Reglamento Interno")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Asegurar UNA sola fila
    cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
    regla = cursor.fetchone()

    if not regla:
        cursor.execute("""
            INSERT INTO reglas_grupo (Id_Grupo) VALUES (1)
        """)
        con.commit()
        cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
        regla = cursor.fetchone()

    id_regla = regla["id_regla"]

    st.markdown("### 📦 DATOS GENERALES")
    with st.container():
        nombre_grupo = st.text_input("Nombre del grupo:", regla["nombre_grupo"] or "")
        nombre_comunidad = st.text_input("Nombre de la comunidad del grupo:", regla["nombre_comunidad"] or "")
        fecha_formacion = st.date_input("Fecha de formación:", 
                                        value=regla["fecha_formacion"] or date.today())

    st.markdown("### 💰 VALORES ECONÓMICOS")
    with st.container():
        multa_inasistencia = st.number_input("Multa por inasistencia ($):", value=float(regla["multa_inasistencia"] or 0))
        ahorro_minimo = st.number_input("Ahorro mínimo por reunión ($):", value=float(regla["ahorro_minimo"] or 0))
        interes = st.number_input("Interés por cada $10 prestados (%):", value=float(regla["interes_por_10"] or 0))
        prestamo_max = st.number_input("Préstamo máximo permitido ($):", value=float(regla["prestamo_maximo"] or 0))
        plazo_max = st.number_input("Plazo máximo de pago (meses):", value=int(regla["plazo_maximo"] or 0))

    st.markdown("### 📝 PERMISOS DE INASISTENCIA")
    st.info("No pagamos una multa si faltamos a una reunión y tenemos permiso por la siguiente razón (o razones):")
    permisos = st.text_area("Permisos válidos de inasistencia:", regla["permisos_inasistencia"] or "")

    st.markdown("### 📅 CICLO DEL GRUPO")
    with st.container():
        ciclo_inicio = st.date_input("Fecha de inicio del ciclo:", value=regla["ciclo_inicio"] or date.today())
        ciclo_fin = st.date_input("Fecha de fin del ciclo:", value=regla["ciclo_fin"] or date.today())

    st.markdown("### 🎯 META SOCIAL")
    meta_social = st.text_area("Meta social del grupo:", regla["meta_social"] or "")

    st.markdown("### 📌 OTRAS REGLAS")
    otras = st.text_area("Otras reglas adicionales:", regla["otras_reglas"] or "")

    if st.button("💾 Guardar Reglamento"):

        cursor.execute("""
            UPDATE reglas_grupo SET
                nombre_grupo=%s, nombre_comunidad=%s,
                fecha_formacion=%s,
                multa_inasistencia=%s, ahorro_minimo=%s,
                interes_por_10=%s, prestamo_maximo=%s, plazo_maximo=%s,
                permisos_inasistencia=%s,
                ciclo_inicio=%s, ciclo_fin=%s,
                meta_social=%s, otras_reglas=%s
            WHERE id_regla=%s
        """, (
            nombre_grupo, nombre_comunidad,
            fecha_formacion,
            multa_inasistencia, ahorro_minimo,
            interes, prestamo_max, plazo_max,
            permisos,
            ciclo_inicio, ciclo_fin,
            meta_social, otras,
            id_regla
        ))

        con.commit()

        st.success("✔ Reglamento actualizado correctamente.")
        mostrar_resumen(
            nombre_grupo, nombre_comunidad, fecha_formacion,
            multa_inasistencia, ahorro_minimo, interes,
            prestamo_max, plazo_max,
            permisos, ciclo_inicio, ciclo_fin,
            meta_social, otras
        )

    cursor.close()
    con.close()


# ============================================================
# RESUMEN VISUAL DEL REGLAMENTO
# ============================================================
def mostrar_resumen(
    nombre_grupo, nombre_comunidad, fecha_formacion,
    multa, ahorro, interes, prestamo_max, plazo_max,
    permisos, ciclo_inicio, ciclo_fin,
    meta_social, otras
):
    st.markdown("---")
    st.markdown("## 📜 Reglamento Interno — Resumen")

    st.markdown(f"""
    <div style="text-align:center; font-size:22px; font-weight:bold;">
        Reglamento Interno del Grupo<br>
        {nombre_grupo}
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:justify; font-size:16px;">
        <br><b>Comunidad:</b> {nombre_comunidad}
        <br><b>Fecha de formación:</b> {fecha_formacion}
        <br><b>Multa por inasistencia:</b> ${multa}
        <br><b>Ahorro mínimo:</b> ${ahorro}
        <br><b>Interés por cada $10:</b> {interes}%
        <br><b>Préstamo máximo:</b> ${prestamo_max}
        <br><b>Plazo máximo:</b> {plazo_max} meses
        <br><br><b>Permisos válidos de inasistencia:</b><br>{permisos}
        <br><br><b>Inicio del ciclo:</b> {ciclo_inicio}
        <br><b>Fin del ciclo:</b> {ciclo_fin}
        <br><br><b>Meta social:</b><br>{meta_social}
        <br><br><b>Otras reglas:</b><br>{otras}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 2. COMITÉ DIRECTIVO (4 CARGOS FIJOS)
# ============================================================
def panel_comite():

    st.header("👥 Comité Directivo del Grupo")
    st.write("Complete los 4 cargos oficiales del comité directivo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
    regla = cursor.fetchone()
    id_regla = regla["id_regla"]

    # Leer comité existente
    cursor.execute("SELECT * FROM comite_directiva WHERE id_regla=%s", (id_regla,))
    filas = cursor.fetchall()

    valores = {
        "Presidenta": "",
        "Secretaria": "",
        "Tesorera": "",
        "Llave": ""
    }

    for f in filas:
        valores[f["cargo"]] = f["nombre_socia"]

    st.markdown("### 📦 Ingreso de cargos")

    presidenta = st.text_input("Presidenta:", valores["Presidenta"])
    secretaria = st.text_input("Secretaria:", valores["Secretaria"])
    tesorera = st.text_input("Tesorera:", valores["Tesorera"])
    llave = st.text_input("Llave:", valores["Llave"])

    if st.button("💾 Guardar Comité"):

        cursor.execute("DELETE FROM comite_directiva WHERE id_regla=%s", (id_regla,))

        datos = {
            "Presidenta": presidenta,
            "Secretaria": secretaria,
            "Tesorera": tesorera,
            "Llave": llave
        }

        for cargo, nombre in datos.items():
            if nombre.strip() != "":
                cursor.execute("""
                    INSERT INTO comite_directiva (id_regla, cargo, nombre_socia)
                    VALUES (%s, %s, %s)
                """, (id_regla, cargo, nombre))

        con.commit()
        st.success("✔ Comité actualizado correctamente.")
        st.rerun()

    cursor.close()
    con.close()


# ============================================================
# 3. EXPORTAR PDF
# ============================================================
def exportar_pdf():

    st.header("📄 Exportar Reglamento a PDF")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo LIMIT 1")
    regla = cursor.fetchone()

    cursor.execute("SELECT * FROM comite_directiva WHERE id_regla=%s", (regla["id_regla"],))
    comite = cursor.fetchall()

    archivo = "reglamento.pdf"
    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    contenido = []

    contenido.append(Paragraph(f"<b>REGLAMENTO INTERNO DEL GRUPO</b>", styles["Title"]))
    contenido.append(Paragraph("<br/>", normal))

    contenido.append(Paragraph(f"<b>Nombre del Grupo:</b> {regla['nombre_grupo']}", normal))
    contenido.append(Paragraph(f"<b>Comunidad:</b> {regla['nombre_comunidad']}", normal))
    contenido.append(Paragraph(f"<b>Fecha de Formación:</b> {regla['fecha_formacion']}", normal))
    contenido.append(Paragraph(f"<b>Inicio del Ciclo:</b> {regla['ciclo_inicio']}", normal))
    contenido.append(Paragraph(f"<b>Fin del Ciclo:</b> {regla['ciclo_fin']}", normal))

    contenido.append(Paragraph("<br/><b>VALORES ECONÓMICOS</b>", normal))
    contenido.append(Paragraph(f"Multa por inasistencia: ${regla['multa_inasistencia']}", normal))
    contenido.append(Paragraph(f"Ahorro mínimo: ${regla['ahorro_minimo']}", normal))
    contenido.append(Paragraph(f"Interés: {regla['interes_por_10']}%", normal))
    contenido.append(Paragraph(f"Préstamo máximo: ${regla['prestamo_maximo']}", normal))
    contenido.append(Paragraph(f"Plazo máximo: {regla['plazo_maximo']} meses", normal))

    contenido.append(Paragraph("<br/><b>PERMISOS DE INASISTENCIA</b>", normal))
    contenido.append(Paragraph(regla["permisos_inasistencia"] or "", normal))

    contenido.append(Paragraph("<br/><b>META SOCIAL</b>", normal))
    contenido.append(Paragraph(regla["meta_social"] or "", normal))

    contenido.append(Paragraph("<br/><b>OTRAS REGLAS</b>", normal))
    contenido.append(Paragraph(regla["otras_reglas"] or "", normal))

    contenido.append(Paragraph("<br/><b>COMITÉ DIRECTIVO</b>", normal))
    for c in comite:
        contenido.append(Paragraph(f"{c['cargo']}: {c['nombre_socia']}", normal))

    pdf = SimpleDocTemplate(archivo, pagesize=letter)
    pdf.build(contenido)

    with open(archivo, "rb") as f:
        st.download_button("📥 Descargar Reglamento PDF", f, file_name="reglamento.pdf")

    cursor.close()
    con.close()
