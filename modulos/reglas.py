import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter



# ============================================================
# FUNCIÓN PRINCIPAL DEL MÓDULO
# ============================================================
def gestionar_reglas():
    st.header("📘 Reglas Internas del Grupo de Ahorro")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Buscar si ya existen reglas
    cursor.execute("SELECT * FROM reglas_grupo ORDER BY id_regla DESC LIMIT 1")
    reglas = cursor.fetchone()

    if reglas:
        mostrar_reglas(reglas)
    else:
        st.info("Aún no hay reglas registradas. Complete el siguiente formulario:")
        crear_reglas()

    cursor.close()
    con.close()



# ============================================================
# CREAR REGLAS INTERNAS
# ============================================================
def crear_reglas():
    with st.form("form_reglas"):

        st.subheader("📝 Información general")
        nombre_grupo = st.text_input("Nombre del grupo de ahorro")
        comunidad = st.text_input("Nombre de la comunidad")
        fecha_formacion = st.date_input("Fecha de formación")

        st.subheader("💰 Ahorros y multas")
        multa = st.number_input("Multa por inasistencia ($)", min_value=0.0)
        ahorro_minimo = st.number_input("Ahorro mínimo ($)", min_value=0.0)

        st.subheader("💵 Préstamos")
        interes = st.number_input("Interés por cada $10 prestados (%)", min_value=0.0)
        prestamo_maximo = st.number_input("Monto máximo de préstamo", min_value=0.0)
        plazo_maximo = st.number_input("Plazo máximo del préstamo (meses)", min_value=1)

        st.subheader("🔁 Ciclo del grupo")
        ciclo_inicio = st.date_input("Inicio del ciclo")
        ciclo_fin = st.date_input("Fin del ciclo")

        st.subheader("🎯 Meta social")
        meta = st.text_area("Meta social")

        otras = st.text_area("Otras reglas")

        enviar = st.form_submit_button("💾 Guardar reglas")

        if enviar:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                INSERT INTO reglas_grupo
                (Id_Grupo, nombre_grupo, nombre_comunidad, fecha_formacion,
                multa_inasistencia, ahorro_minimo, interes_por_10,
                prestamo_maximo, plazo_maximo, ciclo_inicio, ciclo_fin,
                meta_social, otras_reglas)
                VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nombre_grupo, comunidad, fecha_formacion,
                multa, ahorro_minimo, interes,
                prestamo_maximo, plazo_maximo,
                ciclo_inicio, ciclo_fin,
                meta, otras
            ))

            con.commit()
            con.close()

            st.success("Reglas internas registradas correctamente.")
            st.rerun()



# ============================================================
# MOSTRAR REGLAS INTERNAS
# ============================================================
def mostrar_reglas(reglas):

    st.subheader("📌 Información General")
    st.write(f"**Nombre del grupo:** {reglas['nombre_grupo']}")
    st.write(f"**Comunidad:** {reglas['nombre_comunidad']}")
    st.write(f"**Fecha de formación:** {reglas['fecha_formacion']}")

    st.subheader("💰 Ahorros y Multas")
    st.write(f"- Multa por inasistencia: **${reglas['multa_inasistencia']}**")
    st.write(f"- Ahorro mínimo obligatorio: **${reglas['ahorro_minimo']}**")

    st.subheader("💵 Reglas de Préstamo")
    st.write(f"- Interés por cada $10 prestados: **{reglas['interes_por_10']}%**")
    st.write(f"- Monto máximo del préstamo: **${reglas['prestamo_maximo']}**")
    st.write(f"- Plazo máximo del préstamo: **{reglas['plazo_maximo']} meses**")

    st.subheader("🔁 Ciclo del Grupo")
    st.write(f"- Inicio del ciclo: {reglas['ciclo_inicio']}")
    st.write(f"- Fin del ciclo: {reglas['ciclo_fin']}")

    st.subheader("🎯 Meta Social")
    st.write(reglas["meta_social"])

    st.subheader("📄 Otras reglas")
    st.write(reglas["otras_reglas"])

    st.markdown("---")

    # =====================================
    #   PANEL DEL COMITÉ DIRECTIVO
    # =====================================
    mostrar_comite(reglas)

    st.markdown("---")

    # =====================================
    #   PANEL DE PERMISOS DE INASISTENCIA
    # =====================================
    mostrar_permisos(reglas)

    st.markdown("---")

    # =====================================
    #   EDITOR DE REGLAS INTERNAS
    # =====================================
    editor_reglas(reglas)

    st.markdown("---")

    # =====================================
    #   EXPORTAR PDF
    # =====================================
    exportar_pdf(reglas)




# ============================================================
# COMITÉ DIRECTIVO
# ============================================================
def mostrar_comite(reglas):

    st.subheader("👩‍💼 Comité Directivo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cargo = st.selectbox(
        "Cargo",
        ["Presidenta", "Secretaria", "Tesorera", "Responsable de llave", "Otro"]
    )

    nombre = st.text_input("Nombre de la socia")

    if st.button("➕ Agregar integrante"):
        cursor.execute("""
            INSERT INTO comite_directiva (Id_Regla, cargo, nombre_socia)
            VALUES (%s, %s, %s)
        """, (reglas["id_regla"], cargo, nombre))
        con.commit()
        st.success("Integrante agregado.")
        st.rerun()

    cursor.execute("""
        SELECT cargo, nombre_socia
        FROM comite_directiva
        WHERE Id_Regla=%s
    """, (reglas["id_regla"],))
    comite = cursor.fetchall()

    if comite:
        st.table(comite)

    cursor.close()
    con.close()




# ============================================================
# PERMISOS DE INASISTENCIA
# ============================================================
def mostrar_permisos(reglas):

    st.subheader("📝 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    permiso = st.text_input("Agregar nuevo permiso")

    if st.button("➕ Registrar permiso"):
        cursor.execute("""
            INSERT INTO reglas_permisos_inasistencia (Id_Regla, descripcion)
            VALUES (%s, %s)
        """, (reglas["id_regla"], permiso))
        con.commit()
        st.success("Permiso registrado.")
        st.rerun()

    cursor.execute("""
        SELECT descripcion
        FROM reglas_permisos_inasistencia
        WHERE Id_Regla=%s
    """, (reglas["id_regla"],))
    lista = cursor.fetchall()

    if lista:
        st.table(lista)

    cursor.close()
    con.close()




# ============================================================
# EDITOR DE REGLAS INTERNAS
# ============================================================
def editor_reglas(reglas):

    st.subheader("✏️ Editar Reglas Internas")

    if st.checkbox("Mostrar editor"):

        nueva_multa = st.number_input("Nueva multa ($)", value=reglas["multa_inasistencia"])
        nuevo_ahorro = st.number_input("Nuevo ahorro mínimo ($)", value=reglas["ahorro_minimo"])
        nuevo_interes = st.number_input("Nuevo interés por cada $10", value=reglas["interes_por_10"])
        nueva_meta = st.text_area("Meta social", value=reglas["meta_social"])
        nuevas_otras = st.text_area("Otras reglas", value=reglas["otras_reglas"])

        if st.button("💾 Guardar cambios"):
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                UPDATE reglas_grupo
                SET multa_inasistencia=%s,
                    ahorro_minimo=%s,
                    interes_por_10=%s,
                    meta_social=%s,
                    otras_reglas=%s
                WHERE id_regla=%s
            """, (
                nueva_multa, nuevo_ahorro, nuevo_interes,
                nueva_meta, nuevas_otras,
                reglas["id_regla"]
            ))

            con.commit()
            con.close()

            st.success("Reglas actualizadas.")
            st.rerun()




# ============================================================
# EXPORTACIÓN A PDF
# ============================================================
def exportar_pdf(reglas):

    st.subheader("📄 Exportar a PDF")

    if st.button("📥 Generar PDF"):

        crear_pdf_reglas(reglas)

        with open("reglas_internas.pdf", "rb") as pdf:
            st.download_button(
                "📥 Descargar PDF",
                data=pdf,
                file_name="reglas_internas.pdf",
                mime="application/pdf"
            )

        st.success("PDF generado correctamente.")



def crear_pdf_reglas(reglas):

    c = canvas.Canvas("reglas_internas.pdf", pagesize=letter)
    y = 750

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "REGLAS INTERNAS DEL GRUPO")
    y -= 30

    c.setFont("Helvetica", 10)

    for campo, valor in reglas.items():
        c.drawString(50, y, f"{campo}: {valor}")
        y -= 15
        if y < 50:
            c.showPage()
            y = 750

    c.save()
