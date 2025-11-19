import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_promotora():

    rol = st.session_state.get("rol", "")

    # Acceso exclusivo
    if rol != "Promotora":
        st.error("⛔ No tiene permisos para acceder al panel de promotora.")
        return

    st.title("👩‍💼 Panel de Promotora")
    st.info("Funciones disponibles para la promotora.")

    opciones = [
        "Consultar grupos asignados",
        "Validar información financiera",
        "Reportes consolidados"
    ]

    seleccion = st.sidebar.selectbox("Seleccione una opción", opciones)

    if seleccion == "Consultar grupos asignados":
        consultar_grupos()

    elif seleccion == "Validar información financiera":
        validar_finanzas()

    elif seleccion == "Reportes consolidados":
        reportes()


def consultar_grupos():
    st.header("👥 Grupos Asignados")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Grupo")
    grupos = cursor.fetchall()

    if not grupos:
        st.warning("No hay grupos registrados.")
        return

    for g in grupos:
        st.subheader(g["Nombre_Grupo"])
        st.write(f"ID: {g['Id_Grupo']}")
        st.write(f"Inicio: {g['Fecha_Inicio']}")
        st.write(f"Periodicidad: {g['Periodicidad']}")
        st.markdown("---")


def validar_finanzas():
    st.header("📑 Validación Financiera")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM `Préstamo`")   # ← tabla correcta
        prestamos = cursor.fetchall()

        if not prestamos:
            st.info("No se encontraron préstamos registrados.")
            return

        for p in prestamos:
            st.write(f"🆔 ID Préstamo: {p['Id_Prestamo']}")
            st.write(f"💵 Monto: {p['Monto']}")
            st.write(f"📌 Estado: {p['Estado']}")
            st.markdown("---")

    except Exception as e:
        st.error(f"⚠ Error al consultar tabla Préstamo: {e}")

