import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL
# ---------------------------------------------------------
def interfaz_directiva():

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia y multas.")

    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    menu = st.sidebar.radio(
        "Seleccione una sección:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()
    else:
        pagina_multas()


# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA  (SIN CAMBIOS)
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("No se pudo conectar a la BD.")
        return

    cursor = con.cursor()

    fecha = st.date_input("📅 Fecha de reunión", value=date.today())

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"Reunión creada (ID {id_reunion}).")

    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    registros = cursor.fetchall()

    socias = {fila[1]: {"id": fila[0], "sexo": fila[2]} for fila in registros}

    nombre = st.selectbox("👩 Socia:", list(socias.keys()))
    id_socia = socias[nombre]["id"]
    genero = socias[nombre]["sexo"]

    st.text_input("Género:", genero, disabled=True)
    estado = st.selectbox("📍 Estado:", ["Presente", "Ausente"])

    if st.button("💾 Guardar asistencia"):

        cursor.execute("""
            SELECT Id_Asistencia 
            FROM Asistencia 
            WHERE Id_Reunion = %s AND Id_Socia = %s
        """, (id_reunion, id_socia))

        existe = cursor.fetchone()

        if existe:
            st.warning("⚠ Esta socia ya tiene asistencia registrada para esta reunión.")
            return

        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero, fecha))

            con.commit()
            st.success("Asistencia registrada correctamente.")

        except Exception as e:
            st.error(f"Error: {e}")

    cursor.execute("""
        SELECT S.Nombre, A.Genero, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))

    tabla = cursor.fetchall()

    st.subheader("📋 Registro actual")
    if tabla:
        df = pd.DataFrame(tabla, columns=["Socia", "Género", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("Aún no hay asistencia registrada.")


# ---------------------------------------------------------
# 🟥 APLICACIÓN Y CONTROL DE MULTAS (TABLA ORIGINAL + FILTROS + UPDATE)
# ---------------------------------------------------------
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    # ============================
    # REGISTRO DE MULTA
    # ============================
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

    monto = st.number_input("💵 Monto de la multa:", min_value=0.01, step=0.50, format="%.2f")
    fecha = st.date_input("📅 Fecha de aplicación")
    estado = st.selectbox("📍 Estado del pago:", ["A pagar", "Pagada"])

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

    # ============================
    # FILTROS
    # ============================
    st.subheader("🔎 Filtrar multas registradas")

    filtro_socia = st.selectbox("Filtrar por socia:", ["Todas"] + list(lista_socias.keys()))
    filtro_estado = st.selectbox("Filtrar por estado:", ["Todos", "A pagar", "Pagada"])
    filtro_fecha = st.date_input("Filtrar por fecha:", value=None)

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

    # ============================
    # TABLA EXACTA + CAMBIO DE ESTADO
    # ============================
    st.subheader("📋 Multas registradas")

    if multas:
        df = pd.DataFrame(
            multas,
            columns=["ID", "Socia", "Tipo multa", "Monto ($)", "Estado", "Fecha"]
        )

        # Copia editable
        df_editable = df.copy()

        # Crear inputs de edición para estado
        for i in range(len(df)):
            df_editable.at[i, "Estado"] = st.selectbox(
                f"Estado para ID {df.at[i,'ID']}:",
                ["A pagar", "Pagada"],
                index=0 if df.at[i, "Estado"] == "A pagar" else 1,
                key=f"estado_{df.at[i,'ID']}"
            )

        # Mostrar tabla EXACTA sin cambios visuales
        st.dataframe(df)

        # Guardar cambios
        if st.button("💾 Guardar cambios en estados"):
            for i in range(len(df)):
                nuevo_estado = df_editable.at[i, "Estado"]
                id_multa = df.at[i, "ID"]

                if nuevo_estado != df.at[i, "Estado"]:
                    cursor.execute("""
                        UPDATE Multa
                        SET Estado = %s
                        WHERE Id_Multa = %s
                    """, (nuevo_estado, id_multa))

            con.commit()
            st.success("Estados actualizados correctamente.")
            st.rerun()

    else:
        st.info("No hay multas registradas con esos filtros.")

