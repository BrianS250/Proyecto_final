import streamlit as st
from modulos.conexion import obtener_conexion


# ===============================================================
# OBTENER ID DE PROMOTORA BASADO EN EL USUARIO QUE INICIÓ SESIÓN
# ===============================================================
def obtener_id_promotora(usuario):
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT Id_Promotora 
        FROM Promotora 
        WHERE Nombre = %s
    """, (usuario,))

    fila = cursor.fetchone()
    return fila["Id_Promotora"] if fila else None


# ===============================================================
# PANEL PRINCIPAL DE PROMOTORA
# ===============================================================
def interfaz_promotora():

    if st.session_state.get("rol") != "Promotora":
        st.error("⛔ No tiene permisos para acceder al panel de promotora.")
        return

    st.title("👩‍💼 Panel de Promotora")
    st.info("Funciones disponibles para la promotora.")

    # OPCIONES DEL PANEL
    tabs = ["Gestión de grupos"]
    seleccion = st.sidebar.selectbox("Seleccione una opción", tabs)

    if seleccion == "Gestión de grupos":
        gestion_grupos()


# ===============================================================
# GESTIÓN DE GRUPOS (PANTALLA PRINCIPAL)
# ===============================================================
def gestion_grupos():
    st.header("⚙️ Gestión de Grupos")

    sub_opciones = st.tabs(["➕ Crear grupo", "✏️ Editar / Eliminar", "📋 Ver grupos"])

    with sub_opciones[0]:
        crear_grupo()

    with sub_opciones[1]:
        editar_eliminar_grupo()

    with sub_opciones[2]:
        ver_grupos()


# ===============================================================
# CREAR GRUPO
# ===============================================================
def crear_grupo():
    st.subheader("➕ Crear nuevo grupo")

    usuario = st.session_state["usuario"]
    id_promotora = obtener_id_promotora(usuario)

    nombre = st.text_input("Nombre del grupo")
    fecha = st.date_input("Fecha de inicio")
    periodicidad = st.selectbox("Periodicidad", ["Semanal", "Quincenal", "Mensual"])

    if st.button("Guardar grupo"):
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO Grupo (Nombre_Grupo, Fecha_Inicio, Periodicidad, Id_Promotora)
            VALUES (%s, %s, %s, %s)
        """, (nombre, fecha, periodicidad, id_promotora))

        con.commit()
        st.success("Grupo creado correctamente.")
        st.rerun()


# ===============================================================
# EDITAR O ELIMINAR GRUPOS
# ===============================================================
def editar_eliminar_grupo():
    st.subheader("✏️ Editar o eliminar grupo")

    usuario = st.session_state["usuario"]
    id_promotora = obtener_id_promotora(usuario)

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))

    grupos = cursor.fetchall()

    if not grupos:
        st.info("No tienes grupos registrados.")
        return

    # Selección del grupo
    opciones = {f"{g['Nombre_Grupo']} (ID {g['Id_Grupo']})": g for g in grupos}
    seleccion = st.selectbox("Seleccione un grupo", opciones.keys())
    g = opciones[seleccion]

    nuevo_nombre = st.text_input("Nombre del grupo", g["Nombre_Grupo"])
    nueva_fecha = st.date_input("Fecha de inicio", g["Fecha_Inicio"])
    nueva_periodicidad = st.selectbox("Periodicidad", ["Semanal", "Quincenal", "Mensual"],
                                      index=["Semanal","Quincenal","Mensual"].index(g["Periodicidad"]))

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Actualizar grupo"):
            cursor.execute("""
                UPDATE Grupo 
                SET Nombre_Grupo = %s, Fecha_Inicio = %s, Periodicidad = %s
                WHERE Id_Grupo = %s
            """, (nuevo_nombre, nueva_fecha, nueva_periodicidad, g["Id_Grupo"]))
            con.commit()
            st.success("Grupo actualizado correctamente.")
            st.rerun()

    with col2:
        if st.button("🗑️ Eliminar grupo"):
            cursor.execute("DELETE FROM Grupo WHERE Id_Grupo = %s", (g["Id_Grupo"],))
            con.commit()
            st.warning("Grupo eliminado.")
            st.rerun()


# ===============================================================
# VER GRUPOS — CON EXPANDERS (ACORDEÓN)
# ===============================================================
def ver_grupos():
    st.subheader("📋 Ver grupos")

    usuario = st.session_state["usuario"]
    id_promotora = obtener_id_promotora(usuario)

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("""
        SELECT * FROM Grupo
        WHERE Id_Promotora = %s
    """, (id_promotora,))

    grupos = cursor.fetchall()

    if not grupos:
        st.info("No tienes grupos registrados.")
        return

    opciones = {f"{g['Nombre_Grupo']} (ID {g['Id_Grupo']})": g for g in grupos}
    seleccion = st.selectbox("Seleccione un grupo", opciones.keys())

    g = opciones[seleccion]

    # ===========================
    # EXPANDER 1: Info del grupo
    # ===========================
    with st.expander("📘 Información general del grupo", expanded=False):
        st.write(f"### 👥 {g['Nombre_Grupo']}")
        st.write(f"🆔 ID Grupo: {g['Id_Grupo']}")
        st.write(f"📅 Fecha de inicio: {g['Fecha_Inicio']}")
        st.write(f"🔁 Periodicidad: {g['Periodicidad']}")

    # ===========================
    # EXPANDER 2: Validación financiera
    # ===========================
    with st.expander("📑 Validación financiera", expanded=False):

        try:
            cursor.execute("""
                SELECT * FROM `Préstamo`
                WHERE Id_Grupo = %s
            """, (g["Id_Grupo"],))

            prestamos = cursor.fetchall()

            if not prestamos:
                st.info("No se encontraron préstamos para este grupo.")
            else:
                for p in prestamos:
                    st.write(f"🆔 ID Préstamo: {p['Id_Prestamo']}")
                    st.write(f"💵 Monto: {p['Monto']}")
                    st.write(f"📌 Estado: {p['Estado']}")
                    st.markdown("---")

        except Exception as e:
            st.error(f"Error al consultar préstamos: {e}")

    # ===========================
    # EXPANDER 3: Reportes consolidados
    # ===========================
    with st.expander("📊 Reportes consolidados", expanded=False):
        st.info("Aquí se generarán reportes por grupo en futuras versiones.")
