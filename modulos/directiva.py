import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL (CONTROL DE ACCESO)
# ---------------------------------------------------------
def interfaz_directiva():

    rol = st.session_state.get("rol", "").lower()

    # 💠 Título dinámico según el rol
    if rol == "director":
        st.title("👨‍💼 Panel de la Directiva del Grupo")
        st.write("Administre reuniones, asistencia y multas.")
    else:
        st.title("📋 Acceso al sistema")
        st.info("⚠ Acceso limitado. Solo el Director puede administrar asistencia y multas.")
        st.success("Puedes seguir usando otras funciones del sistema.")
        return  # ⛔ NO MOSTRAR MENÚ NI NADA MÁS PARA ADMIN Y PROMOTORA

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Menú SOLO para director
    menu = st.sidebar.radio(
        "Seleccione una sección:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()
    else:
        pagina_multas()


# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT Id_Reunion 
        FROM Reunion 
        WHERE Fecha_reunion = %s
    """, (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        try:
            cursor.execute("""
                INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
                VALUES (%s,'','','',1)
            """, (fecha,))
            con.commit()
            id_reunion = cursor.lastrowid
            st.info(f"Reunión creada (ID {id_reunion}).")
        except:
            st.error("⚠ ERROR: No se pudo crear la reunión. Revise Id_Grupo.")
            return

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")

    asistencia_registro = {}

    col1, col2, col3 = st.columns([1, 3, 3])
    col1.write("**#**")
    col2.write("**Socia**")
    col3.write("**Asistencia (SI / NO)**")

    for idx, (id_socia, nombre) in enumerate(socias, start=1):
        c1, c2, c3 = st.columns([1, 3, 3])

        c1.write(idx)
        c2.write(nombre)

        asistencia = c3.selectbox(
            "",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )

        asistencia_registro[id_socia] = asistencia

    if st.button("💾 Guardar asistencia general"):

        try:
            for id_socia, asistencia in asistencia_registro.items():

                estado = "Presente" if asistencia == "SI" else "Ausente"

                cursor.execute("""
                    SELECT Id_Asistencia 
                    FROM Asistencia 
                    WHERE Id_Reunion = %s AND Id_Socia = %s
                """, (id_reunion, id_socia))

                ya_existe = cursor.fetchone()

                if ya_existe:
                    cursor.execute("""
                        UPDATE Asistencia
                        SET Estado_asistencia = %s, Fecha = %s
                        WHERE Id_Reunion = %s AND Id_Socia = %s
                    """, (estado, fecha, id_reunion, id_socia))
                else:
                    cursor.execute("""
                        INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                        VALUES (%s, %s, %s, %s)
                    """, (id_reunion, id_socia, estado, fecha))

            con.commit()
            st.success("Asistencia guardada correctamente.")

        except Exception as e:
            st.error(f"Error al guardar asistencia: {e}")

    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["Socia", "Asistencia"])
        st.subheader("📋 Registro actual")
        st.dataframe(df)

        total_presentes = df[df["Asistencia"] == "Presente"].shape[0]
        st.success(f"👥 Total presentes: {total_presentes}")
    else:
        st.info("Aún no hay asistencia registrada.")


# ---------------------------------------------------------
# 🟥 APLICACIÓN DE MULTAS
# ---------------------------------------------------------
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {nombre: id_tipo for id_tipo, nombre in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    monto = st.number_input("💵 Monto:", min_value=0.01, step=0.50, format="%.2f")
    fecha_raw = st.date_input("📅 Fecha de aplicación")
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("📍 Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo_multa, id_socia))
            con.commit()
            st.success("Multa registrada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"⚠ Error al guardar multa: {e}")

    st.markdown("---")

    st.subheader("🔎 Filtrar multas")

    filtro_socia = st.selectbox("Filtrar por socia:", ["Todas"] + list(lista_socias.keys()))
    filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "A pagar", "Pagada"])
    filtro_fecha_raw = st.date_input("Filtrar por fecha:", value=None)
    filtro_fecha = filtro_fecha_raw.strftime("%Y-%m-%d") if filtro_fecha_raw else None

    query = """
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1 = 1
    """
    params = []

    if filtro_socia != "Todas":
        query += " AND S.Nombre = %s"
        params.append(filtro_socia)

    if filtro_estado != "Todos":
        query += " AND M.Estado = %s"
        params.append(filtro_estado)

    if filtro_fecha:
        query += " AND M.Fecha_aplicacion = %s"
        params.append(filtro_fecha)

    query += " ORDER BY M.Id_Multa DESC"
    cursor.execute(query, params)

    multas = cursor.fetchall()

    st.subheader("📋 Multas registradas")

    if multas:

        cols = st.columns([1,3,3,2,2,2,2])
        cols[0].write("**ID**")
        cols[1].write("**Socia**")
        cols[2].write("**Tipo multa**")
        cols[3].write("**Monto ($)**")
        cols[4].write("**Estado**")
        cols[5].write("**Fecha**")
        cols[6].write("**Acción**")

        for row in multas:
            id_multa, socia, tipo, monto, estado_actual, fecha = row
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1,3,3,2,2,2,2])

            col1.write(id_multa)
            col2.write(socia)
            col3.write(tipo)
            col4.write(f"${monto}")

            nuevo_estado = col5.selectbox(
                "",
                ["A pagar", "Pagada"],
                index=0 if estado_actual == "A pagar" else 1,
                key=f"estado_{id_multa}"
            )

            col6.write(str(fecha))

            if col7.button("Actualizar", key=f"btn_{id_multa}"):
                cursor.execute("""
                    UPDATE Multa
                    SET Estado = %s
                    WHERE Id_Multa = %s
                """, (nuevo_estado, id_multa))
                con.commit()
                st.success(f"Estado actualizado.")
                st.rerun()

    else:
        st.info("No hay multas registradas.")
