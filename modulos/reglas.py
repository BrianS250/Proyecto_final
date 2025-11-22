import streamlit as st
from modulos.conexion import obtener_conexion
from modulos.reglas_utils import obtener_reglas
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# -------------------------------------------------------------------
#  PANEL COMPLETO DE REGLAS INTERNAS
# -------------------------------------------------------------------
def gestionar_reglas():

    st.title("📘 Reglas internas del grupo")

    menu = st.radio(
        "Seleccione una sección:",
        ["Editor de reglas internas", "Comité directivo", "Permisos válidos", "Exportar PDF"],
        horizontal=True
    )

    if menu == "Editor de reglas internas":
        editar_reglamento()

    elif menu == "Comité directivo":
        editar_comite()

    elif menu == "Permisos válidos":
        editar_permisos()

    elif menu == "Exportar PDF":
        exportar_pdf()


# -------------------------------------------------------------------
#  1. EDITOR DE REGLAMENTO
# -------------------------------------------------------------------
def editar_reglamento():

    st.header("📘 Editor general del reglamento")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    reglas = obtener_reglas()

    # -------------------------------------------------------------------
    # Formulario con los campos reales del documento
    # -------------------------------------------------------------------
    nombre_grupo = st.text_input("Nombre del grupo", reglas["nombre_grupo"] if reglas else "")
    comunidad = st.text_input("Nombre de la comunidad del grupo", reglas["comunidad"] if reglas else "")
    fecha_formacion = st.date_input("Fecha de formación", reglas["fecha_formacion"] if reglas and reglas["fecha_formacion"] else None)

    st.subheader("Reuniones")
    dia = st.text_input("Día", reglas["dia"] if reglas else "")
    hora = st.text_input("Hora", reglas["hora"] if reglas else "")
    lugar = st.text_input("Lugar", reglas["lugar"] if reglas else "")
    frecuencia = st.text_input("Frecuencia", reglas["frecuencia"] if reglas else "")

    st.subheader("Asistencia y Multas")
    multa_inasistencia = st.number_input("Multa por inasistencia ($)", min_value=0.25, step=0.25,
                                         value=float(reglas["multa_inasistencia"]) if reglas else 0.25)

    st.subheader("Ahorro")
    ahorro_minimo = st.number_input("Cantidad mínima de ahorro ($)", min_value=0.25, step=0.25,
                                    value=float(reglas["ahorro_minimo"]) if reglas else 1)

    st.subheader("Préstamos")
    interes_por_10 = st.number_input("Tasa de interés por cada $10 (%)",
                                     min_value=0.1,
                                     value=float(reglas["interes_por_10"]) if reglas else 1)

    prestamo_maximo = st.number_input("Monto máximo de préstamo ($)", min_value=1.0,
                                     value=float(reglas["prestamo_maximo"]) if reglas else 100)

    plazo_maximo = st.number_input("Plazo máximo de préstamo (meses)", min_value=1,
                                   value=int(reglas["plazo_maximo"]) if reglas else 6)

    st.subheader("Ciclo")
    ciclo_inicio = st.date_input("Fecha de inicio de ciclo",
                                 reglas["ciclo_inicio"] if reglas and reglas["ciclo_inicio"] else None)

    ciclo_fin = st.date_input("Fecha de fin de ciclo",
                              reglas["ciclo_fin"] if reglas and reglas["ciclo_fin"] else None)

    meta_social = st.text_area("Meta social del grupo", reglas["meta_social"] if reglas else "", height=150)

    otras_reglas = st.text_area("Otras reglas adicionales:", reglas["otras_reglas"] if reglas else "", height=150)

    # -------------------------------------------------------------------
    # Guardar / actualizar
    # -------------------------------------------------------------------
    if st.button("💾 Guardar cambios"):

        # Si no existen reglas → insertar
        if not reglas:
            cursor.execute("""
                INSERT INTO reglas_grupo (
                    nombre_grupo, comunidad, fecha_formacion, dia, hora, lugar, frecuencia,
                    multa_inasistencia, ahorro_minimo, interes_por_10, prestamo_maximo, plazo_maximo,
                    ciclo_inicio, ciclo_fin, meta_social, otras_reglas
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (nombre_grupo, comunidad, fecha_formacion, dia, hora, lugar, frecuencia,
                  multa_inasistencia, ahorro_minimo, interes_por_10, prestamo_maximo, plazo_maximo,
                  ciclo_inicio, ciclo_fin, meta_social, otras_reglas))
            con.commit()
        else:
            cursor.execute("""
                UPDATE reglas_grupo SET
                    nombre_grupo=%s,
                    comunidad=%s,
                    fecha_formacion=%s,
                    dia=%s,
                    hora=%s,
                    lugar=%s,
                    frecuencia=%s,
                    multa_inasistencia=%s,
                    ahorro_minimo=%s,
                    interes_por_10=%s,
                    prestamo_maximo=%s,
                    plazo_maximo=%s,
                    ciclo_inicio=%s,
                    ciclo_fin=%s,
                    meta_social=%s,
                    otras_reglas=%s
                WHERE id_regla=%s
            """, (nombre_grupo, comunidad, fecha_formacion, dia, hora, lugar, frecuencia,
                  multa_inasistencia, ahorro_minimo, interes_por_10, prestamo_maximo, plazo_maximo,
                  ciclo_inicio, ciclo_fin, meta_social, otras_reglas, reglas["id_regla"]))
            con.commit()

        st.success("✔ Reglas actualizadas correctamente.")
        st.rerun()

    con.close()


# -------------------------------------------------------------------
# 2. COMITÉ DIRECTIVO
# -------------------------------------------------------------------
def editar_comite():

    st.header("👩‍💼 Comité directivo — Solo 4 cargos oficiales")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    reglas = obtener_reglas()
    id_regla = reglas["id_regla"] if reglas else None

    cargos = ["Presidenta", "Secretaria", "Tesorera", "Llave"]

    cursor.execute("SELECT * FROM comite_directiva WHERE id_regla=%s", (id_regla,))
    existentes = cursor.fetchall()

    mapa_existentes = {c["cargo"]: c["nombre_socia"] for c in existentes}

    nuevos = {}

    for c in cargos:
        nuevos[c] = st.text_input(c, value=mapa_existentes.get(c, ""))

    if st.button("💾 Guardar comité"):

        cursor.execute("DELETE FROM comite_directiva WHERE id_regla=%s", (id_regla,))
        con.commit()

        for c in cargos:
            if nuevos[c].strip():
                cursor.execute("""
                    INSERT INTO comite_directiva(id_regla, cargo, nombre_socia)
                    VALUES(%s,%s,%s)
                """, (id_regla, c, nuevos[c].strip()))
        con.commit()

        st.success("✔ Comité actualizado.")
        st.rerun()

    con.close()


# -------------------------------------------------------------------
# 3. PERMISOS VÁLIDOS
# -------------------------------------------------------------------
def editar_permisos():
    st.header("📄 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    reglas = obtener_reglas()

    cursor.execute("SELECT * FROM reglas_permisos WHERE id_regla=%s", (reglas["id_regla"],))
    permisos = cursor.fetchall()

    st.info("No pagamos multa si faltamos a una reunión y tenemos permiso por la siguiente razón:")

    nuevos = {}

    for i in range(1, 6):
        campo = f"permiso_{i}"
        nuevos[campo] = st.text_input(f"Razón {i}",
                                      value=permisos[i-1]["descripcion"] if len(permisos) >= i else "")

    if st.button("💾 Guardar permisos"):
        cursor.execute("DELETE FROM reglas_permisos WHERE id_regla=%s", (reglas["id_regla"],))
        con.commit()

        for p in nuevos.values():
            if p.strip():
                cursor.execute("""
                    INSERT INTO reglas_permisos(id_regla, descripcion)
                    VALUES(%s,%s)
                """, (reglas["id_regla"], p))

        con.commit()
        st.success("✔ Permisos actualizados.")
        st.rerun()

    con.close()


# -------------------------------------------------------------------
# 4. EXPORTAR PDF
# -------------------------------------------------------------------
def exportar_pdf():

    st.header("📄 Exportar Reglamento en PDF")

    reglas = obtener_reglas()

    contenido = f"""
    Reglamento del Grupo: {reglas['nombre_grupo']}

    Comunidad: {reglas['comunidad']}
    Fecha formación: {reglas['fecha_formacion']}

    --- Reuniones ---
    Día: {reglas['dia']}
    Hora: {reglas['hora']}
    Lugar: {reglas['lugar']}
    Frecuencia: {reglas['frecuencia']}

    --- Asistencia y Multas ---
    Multa por inasistencia: ${reglas['multa_inasistencia']}

    --- Ahorro ---
    Ahorro mínimo: ${reglas['ahorro_minimo']}

    --- Préstamos ---
    Tasa por cada $10: {reglas['interes_por_10']}%
    Monto máximo: ${reglas['prestamo_maximo']}
    Plazo máximo: {reglas['plazo_maximo']} meses

    --- Ciclo ---
    Inicio: {reglas['ciclo_inicio']}
    Fin: {reglas['ciclo_fin']}

    --- Meta Social ---
    {reglas['meta_social']}

    --- Otras reglas ---
    {reglas['otras_reglas']}
    """

    styles = getSampleStyleSheet()
    pdf_path = "Reglamento_Grupo.pdf"

    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    story = [Paragraph(contenido.replace("\n", "<br/>"), styles["Normal"])]
    pdf.build(story)

    with open(pdf_path, "rb") as f:
        st.download_button("⬇ Descargar PDF", f, file_name="Reglamento_Grupo.pdf", mime="application/pdf")

