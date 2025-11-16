import streamlit as st
from modulos.conexion import obtener_conexion

def interfaz_administrador():
    st.header("🛡️ Panel del Administrador")
    st.write("Gestiona la plataforma, supervisa distritos, empleados y obtén una vista estratégica completa del sistema.")

    menu = st.sidebar.radio(
        "Menú del Administrador:",
        [
            "🏙️ Ver distritos",
            "👥 Ver grupos",
            "🧑‍💼 Ver empleados",
            "📊 Resumen general del sistema"
        ]
    )

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # ------------------------------------------
    # 1. Ver Distritos
    # ------------------------------------------
    if menu == "🏙️ Ver distritos":
        st.subheader("🏙️ Distritos Registrados")
        cursor.execute("SELECT Id_Distrito, Nombre FROM Distrito")
        filas = cursor.fetchall()

        if filas:
            for d in filas:
                st.write(f"🔹 **ID:** {d[0]} — **Distrito:** {d[1]}")
        else:
            st.warning("No existen distritos registrados.")

    # ------------------------------------------
    # 2. Ver Grupos
    # ------------------------------------------
    elif menu == "👥 Ver grupos":
        st.subheader("👥 Grupos registrados")
        cursor.execute("""
            SELECT Grupo.Id_Grupo, Grupo.Nombre, Distrito.Nombre 
            FROM Grupo 
            INNER JOIN Distrito ON Grupo.Id_Distrito = Distrito.Id_Distrito
        """)
        filas = cursor.fetchall()

        if filas:
            for g in filas:
                st.write(f"🔸 **Grupo:** {g[1]} — **Distrito:** {g[2]} (ID {g[0]})")
        else:
            st.warning("No hay grupos registrados.")

    # ------------------------------------------
    # 3. Ver Empleados
    # ------------------------------------------
    elif menu == "🧑‍💼 Ver empleados":
        st.subheader("🧑‍💼 Empleados del sistema")
        cursor.execute("SELECT Id_Empleado, Usuario, Rol FROM Empleado")
        filas = cursor.fetchall()

        if filas:
            for e in filas:
                rol_icon = "👑" if e[2].lower() == "administrador" else "👤"
                st.write(f"{rol_icon} **Usuario:** {e[1]} — **Rol:** {e[2]} (ID {e[0]})")
        else:
            st.warning("No hay empleados registrados.")

    # ------------------------------------------
    # 4. Resumen General
    # ------------------------------------------
    elif menu == "📊 Resumen general del sistema":
        st.subheader("📊 Indicadores Generales del Sistema")

        # Total Distritos
        cursor.execute("SELECT COUNT(*) FROM Distrito")
        total_distritos = cursor.fetchone()[0]

        # Total Grupos
        cursor.execute("SELECT COUNT(*) FROM Grupo")
        total_grupos = cursor.fetchone()[0]

        # Total Empleados
        cursor.execute("SELECT COUNT(*) FROM Empleado")
        total_empleados = cursor.fetchone()[0]

        # Total Préstamos o Pagos
        cursor.execute("SELECT COUNT(*) FROM Prestamo")
        total_prestamos = cursor.fetchone()[0]

        st.info(f"🏙️ **Distritos:** {total_distritos}")
        st.info(f"👥 **Grupos:** {total_grupos}")
        st.info(f"🧑‍💼 **Empleados:** {total_empleados}")
        st.info(f"💰 **Movimientos financieros registrados:** {total_prestamos}")

        st.success("📌 Vista estratégica general del sistema actualizada.")

