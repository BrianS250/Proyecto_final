import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from modulos.conexion import obtener_conexion


# ======================================================================
# PANEL PRINCIPAL DE REGLAS
# ======================================================================
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


# ======================================================================
# 1. EDITOR DE REGLAS INTERNAS (TABLA reglas_grupo)
# ======================================================================
def editor_reglas():
    st.subheader("📘 Editor de reglas internas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo ORDER BY id_regla ASC")
    reglas = cursor.fetchall()

    # Si no existen reglas → crear primera fila
    if not reglas:
        cursor.execute("INSERT INTO reglas_grupo (nombre_grupo, nombre_comunidad) VALUES ('', '')")
        con.commit()
        cursor.execute("SELECT * FROM reglas_grupo ORDER BY id_regla ASC")
        reglas = cursor.fetchall()

    regla = reglas[0]  # siempre hay solo una fila

    st.write("### Valores generales del grupo")

    nombre_grupo = st.text_input("Nombre del Grupo", regla["nombre_grupo"])
    comunidad = st.text_input("Comunidad", regla["nombre_comunidad"])
    multa_inasistencia = st.number_input("Multa por inasistencia", value=float(regla["multa_inasistencia"]))
    ahorro_minimo = st.number_input("Ahorro mínimo", value=float(regla["ahorro_minimo"]))
    interes10 = st.number_input("Interés por cada $10 prestados (%)", value=float(regla["interes_por_10"]))
    prestamo_maximo = st.number_input("Préstamo máximo", value=float(regla["prestamo_maximo"]))
    plazo_maximo = st.number_input("Plazo máximo (meses)", value=int(regla["plazo_maximo"]))
    otras_reglas = st.text_area("Otras reglas", regla["otras_reglas"] or "")

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
            WHERE id_regla=%s
        """, (
            nombre_grupo,
            comunidad,
            multa_inasistencia,
            ahorro_minimo,
            interes10,
            prestamo_maximo,
            plazo_maximo,
            otras_reglas,
            regla["id_regla"]
        ))

        con.commit()
        st.success("Cambios guardados correctamente.")
        st.rerun()

    cursor.close()
    con.close()


# ======================================================================
# 2. COMITÉ DIRECTIVO  (TABLA comite_directiva)
# ======================================================================
def mostrar_comite():
    st.subheader("👩‍💼 Comité directivo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM comite_directiva ORDER BY id_comite ASC")
    filas = cursor.fetchall()

    st.write("### Registrar nuevo miembro del comité")

    nombre_socia = st.text_input("Nombre de la socia:")
    cargo = st.text_input("Cargo:")

    if st.button("➕ Agregar"):
        if nombre_socia.strip() != "" and cargo.strip() != "":
            cursor.execute("""
                INSERT INTO comite_directiva (nombre_socia, cargo)
                VALUES (%s, %s)
            """, (nombre_socia, cargo))
            con.commit()
            st.success("Miembro agregado.")
            st.rerun()
        else:
            st.warning("Debe ingresar todos los campos.")

    st.write("### Miembros actuales")

    for fila in filas:
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(f"**{fila['nombre_socia']}**")
        col2.write(fila["cargo"])
        if col3.button("Eliminar", key=f"del_c{fila['id_comite']}"):
            cursor.execute("DELETE FROM comite_directiva WHERE id_comite=%s", (fila["id_comite"],))
            con.commit()
            st.rerun()

    cursor.close()
    con.close()


# ======================================================================
# 3. PERMISOS DE INASISTENCIA (TABLA regla_permisos_inasistencia)
# ======================================================================
def mostrar_permisos():
    st.subheader("📝 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    nuevo = st.text_input("Agregar nuevo permiso:")

    if st.button("➕ Registrar permiso"):
        if nuevo.strip() != "":
            cursor.execute("""
                INSERT INTO regla_permisos_inasistencia (descripcion)
                VALUES (%s)
            """, (nuevo,))
            con.commit()
            st.success("Permiso registrado.")
            st.rerun()

    st.write("### Permisos registrados")

    cursor.execute("SELECT * FROM regla_permisos_inasistencia ORDER BY id_permiso ASC")
    permisos = cursor.fetchall()

    if permisos:
        for permiso in permisos:
            col1, col2 = st.columns([4, 1])
            col1.write(f"• {permiso['descripcion']}")
            if col2.button("Eliminar", key=f"del_p{permiso['id_permiso']}"):
                cursor.execute("DELETE FROM regla_permisos_inasistencia WHERE id_permiso=%s", (permiso["id_permiso"],))
                con.commit()
                st.rerun()
    else:
        st.info("No hay permisos registrados.")

    cursor.close()
    con.close()


# ======================================================================
# 4. EXPORTAR PDF CON TODAS LAS REGLAS
# ======================================================================
def exportar_pdf():
    st.subheader("📄 Exportar todas las reglas en PDF")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM reglas_grupo ORDER BY id_regla ASC")
    reglas = cursor.fetchall()

    cursor.execute("SELECT * FROM comite_directiva ORDER BY id_comite ASC")
    comite = cursor.fetchall()

    cursor.execute("SELECT * FROM regla_permisos_inasistencia ORDER BY id_permiso ASC")
    permisos = cursor.fetchall()

    buffer = []

    styles = getSampleStyleSheet()
    estilo = styles["Normal"]

    buffer.append(Paragraph("REGLAMENTO INTERNO DEL GRUPO", styles["Title"]))
    buffer.append(Paragraph("<br/>", estilo))

    if reglas:
        r = reglas[0]
        buffer.append(Paragraph(f"<b>Nombre del Grupo:</b> {r['nombre_grupo']}", estilo))
        buffer.append(Paragraph(f"<b>Comunidad:</b> {r['nombre_comunidad']}", estilo))
        buffer.append(Paragraph(f"<b>Multa por inasistencia:</b> ${r['multa_inasistencia']}", estilo))
        buffer.append(Paragraph(f"<b>Ahorro mínimo:</b> ${r['ahorro_minimo']}", estilo))
        buffer.append(Paragraph(f"<b>Interés por cada $10:</b> {r['interes_por_10']}%", estilo))
        buffer.append(Paragraph(f"<b>Préstamo máximo:</b> ${r['prestamo_maximo']}", estilo))
        buffer.append(Paragraph(f"<b>Plazo máximo:</b> {r['plazo_maximo']} meses", estilo))
        buffer.append(Paragraph(f"<b>Otras reglas:</b><br/>{r['otras_reglas']}", estilo))

    buffer.append(Paragraph("<br/><b>COMITÉ DIRECTIVO</b>", estilo))
    for c in comite:
        buffer.append(Paragraph(f"{c['nombre_socia']} — {c['cargo']}", estilo))

    buffer.append(Paragraph("<br/><b>PERMISOS VÁLIDOS DE INASISTENCIA</b>", estilo))
    for p in permisos:
        buffer.append(Paragraph(f"- {p['descripcion']}", estilo))

    # PDF temporal
    archivo = "reglamento_grupo.pdf"
    pdf = SimpleDocTemplate(archivo, pagesize=letter)
    pdf.build(buffer)

    with open(archivo, "rb") as f:
        st.download_button("📥 Descargar PDF", data=f, file_name="reglamento_grupo.pdf")

    cursor.close()
    con.close()
