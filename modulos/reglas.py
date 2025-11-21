import streamlit as st
import mysql.connector
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from modulos.conexion import obtener_conexion


# ===========================================================
# PANTALLA PRINCIPAL DE REGLAS INTERNAS
# ===========================================================
def gestionar_reglas():
    st.title("📘 Reglas internas del grupo")

    opcion = st.radio(
        "Seleccione una sección:",
        [
            "Editor de reglas internas",
            "Comité directivo",
            "Permisos válidos de inasistencia",
            "Exportar reglas en PDF"
        ]
    )

    if opcion == "Editor de reglas internas":
        mostrar_reglas()

    elif opcion == "Comité directivo":
        mostrar_comite()

    elif opcion == "Permisos válidos de inasistencia":
        mostrar_permisos()

    elif opcion == "Exportar reglas en PDF":
        exportar_pdf()



# ===========================================================
# SECCIÓN 1: REGLAS INTERNAS (usas: otras_reglas)
# ===========================================================
def mostrar_reglas():

    st.subheader("📖 Editor de reglas internas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    nueva = st.text_area("Agregar nueva regla:")

    if st.button("➕ Añadir regla"):
        if nueva.strip() != "":
            cursor.execute("""
                UPDATE reglas_grupo 
                SET otras_reglas = CONCAT(
                    IFNULL(otras_reglas, ''), 
                    '\n• ', %s
                )
                WHERE id_regla = 1
            """, (nueva,))
            con.commit()
            st.success("Regla añadida correctamente.")
            st.rerun()

    # Mostrar reglas
    cursor.execute("SELECT otras_reglas FROM reglas_grupo WHERE id_regla = 1")
    fila = cursor.fetchone()

    st.markdown("### 📋 Reglas actuales:")

    if fila and fila["otras_reglas"]:
        st.text(fila["otras_reglas"])
    else:
        st.info("No hay reglas registradas.")

    cursor.close()
    con.close()



# ===========================================================
# SECCIÓN 2: COMITÉ DIRECTIVO (usa: comite_directiva)
# ===========================================================
def mostrar_comite():
    st.subheader("👥 Comité directivo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    st.markdown("### Registrar nuevo miembro")

    cargo = st.text_input("Cargo")
    nombre = st.text_input("Nombre de la socia")

    if st.button("➕ Registrar miembro"):
        cursor.execute("""
            INSERT INTO comite_directiva (id_regla, cargo, nombre_socia)
            VALUES (1, %s, %s)
        """, (cargo, nombre))
        con.commit()
        st.success("Miembro registrado.")
        st.rerun()

    cursor.execute("""
        SELECT id_comite, cargo, nombre_socia 
        FROM comite_directiva 
        ORDER BY id_comite ASC
    """)
    miembros = cursor.fetchall()

    st.markdown("### 📋 Miembros registrados:")
    for m in miembros:
        col1, col2, col3 = st.columns([5, 4, 1])
        col1.write(f"**{m['cargo']}**")
        col2.write(m["nombre_socia"])

        if col3.button("❌", key=f"del_c{m['id_comite']}"):
            cursor.execute("DELETE FROM comite_directiva WHERE id_comite=%s", (m["id_comite"],))
            con.commit()
            st.success("Miembro eliminado.")
            st.rerun()

    cursor.close()
    con.close()



# ===========================================================
# SECCIÓN 3: PERMISOS DE INASISTENCIA (usa: regla_permisos_inasistencia)
# ===========================================================
def mostrar_permisos():

    st.subheader("📝 Permisos válidos de inasistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    permiso = st.text_input("Agregar nuevo permiso")

    if st.button("➕ Registrar permiso"):
        cursor.execute("""
            INSERT INTO regla_permisos_inasistencia (id_regla, descripcion)
            VALUES (1, %s)
        """, (permiso,))
        con.commit()
        st.success("Permiso registrado.")
        st.rerun()

    cursor.execute("""
        SELECT id_permiso, descripcion
        FROM regla_permisos_inasistencia
        ORDER BY id_permiso ASC
    """)
    lista = cursor.fetchall()

    st.markdown("### 📋 Permisos registrados:")
    for p in lista:
        col1, col2 = st.columns([8, 1])
        col1.write(p["descripcion"])

        if col2.button("🗑️", key=f"del_p{p['id_permiso']}"):
            cursor.execute("DELETE FROM regla_permisos_inasistencia WHERE id_permiso=%s", (p["id_permiso"],))
            con.commit()
            st.success("Permiso eliminado.")
            st.rerun()

    cursor.close()
    con.close()



# ===========================================================
# SECCIÓN 4: EXPORTAR PDF (usa: otras_reglas)
# ===========================================================
def exportar_pdf():

    st.subheader("📄 Exportar todas las reglas en PDF")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT otras_reglas FROM reglas_grupo WHERE id_regla = 1")
    fila = cursor.fetchone()

    cursor.close()
    con.close()

    if not fila or fila[0] is None:
        st.warning("No hay reglas para exportar.")
        return

    reglas_texto = fila[0].replace("\n", "<br/>")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer)
    estilos = getSampleStyleSheet()

    contenido = []
    contenido.append(Paragraph("<b>REGLAS INTERNAS DEL GRUPO</b><br/><br/>", estilos["Title"]))
    contenido.append(Paragraph(reglas_texto, estilos["Normal"]))

    doc.build(contenido)
    buffer.seek(0)

    st.success("PDF generado correctamente.")

    st.download_button(
        label="📥 Descargar PDF",
        data=buffer,
        file_name="Reglas_internas.pdf",
        mime="application/pdf"
    )
