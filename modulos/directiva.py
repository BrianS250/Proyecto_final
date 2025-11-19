import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.autorizar_prestamo import autorizar_prestamo   # << IMPORTACIÓN CORRECTA


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL (SOLO DIRECTOR)
# ---------------------------------------------------------
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso al sistema")
        st.warning("⚠️ Acceso restringido. Esta sección es exclusiva para el Director.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, ingresos, multas y préstamos.")

    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # ---------------------------------------------------------
    # 🔵 MENÚ LATERAL (SE AGREGA SOLO UNA LÍNEA)
    # ---------------------------------------------------------
    menu = st.sidebar.radio(
        "Seleccione una sección:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",       # << AGREGADO AQUÍ
            "📄 Generar reporte"
        ]
    )

    # ---------------------------------------------------------
    # 🔵 RUTEO DEL MENÚ (SE AGREGA SOLO UNA OPCIÓN)
    # ---------------------------------------------------------
    if menu == "Registro de asistencia":
        pagina_asistencia()
    elif menu == "Aplicar multas":
        pagina_multas()
    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()
    elif menu == "Autorizar préstamo":    # << AGREGADO AQUÍ
        autorizar_prestamo()
    else:
        pagina_reporte()



# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("No se pudo conectar a la BD.")
        return

    cursor = con.cursor()

    # Selección de fecha
    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Verificar si la reunión existe o crearla
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        try:
            cursor.execute("SHOW COLUMNS FROM Reunion")
            columnas = [col[0] for col in cursor.fetchall()]

            datos = {
                "Fecha_reunion": fecha,
                "observaciones": "",
                "acuerdos": "",
                "Tema_central": "",
                "Id_Grupo": 1
            }

            for col in columnas:
                if col not in datos and col != "Id_Reunion":
                    datos[col] = ""

            cols_sql = ", ".join(datos.keys())
            vals_sql = ", ".join(["%s"] * len(datos))

            cursor.execute(
                f"INSERT INTO Reunion ({cols_sql}) VALUES ({vals_sql})",
                list(datos.values())
            )

            con.commit()
            id_reunion = cursor.lastrowid
            st.info(f"Reunión creada (ID {id_reunion}).")

        except Exception as e:
            st.error(f"⚠ ERROR al crear la reunión: {e}")
            return

    # -------------------------------------------------------------------
    # MOSTRAR SOCIAS
    # -------------------------------------------------------------------
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

    # Guardar asistencia
    if st.button("💾 Guardar asistencia general"):

        try:
            for id_socia, asistencia in asistencia_registro.items():

                estado = "Presente" if asistencia == "SI" else "Ausente"

                cursor.execute(
                    "SELECT Id_Asistencia FROM Asistencia "
                    "WHERE Id_Reunion = %s AND Id_Socia = %s",
                    (id_reunion, id_socia)
                )
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

    # Mostrar registro actual
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

    st.markdown("---")

    # -----------------------------------------------
    # INGRESOS EXTRAORDINARIOS
    # -----------------------------------------------
    st.header("💰 Ingresos extraordinarios de la reunión")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista_socias = cursor.fetchall()
    dict_socias = {nombre: id_socia for id_socia, nombre in lista_socias}

    socia_sel = st.selectbox("👩 Socia que aporta:", dict_socias.keys())
    id_socia_aporta = dict_socias[socia_sel]

    tipo = st.selectbox("Tipo de ingreso:", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción del ingreso (opcional)")
    monto = st.number_input("Monto recibido ($):", min_value=0.00, step=0.50)

    if st.button("➕ Registrar ingreso extraordinario"):
        try:
            cursor.execute("""
                INSERT INTO IngresosExtra (Id_Reunion, Id_Socia, Tipo, Descripcion, Monto, Fecha)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_reunion, id_socia_aporta, tipo, descripcion, monto, fecha))

            con.commit()
            st.success("Ingreso extraordinario registrado con éxito.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar ingreso: {e}")

    cursor.execute("""
        SELECT S.Nombre, I.Tipo, I.Descripcion, I.Monto, I.Fecha
        FROM IngresosExtra I
        JOIN Socia S ON S.Id_Socia = I.Id_Socia
        WHERE I.Id_Reunion = %s
    """, (id_reunion,))
    ingresos = cursor.fetchall()

    if ingresos:
        df_ing = pd.DataFrame(ingresos, columns=["Socia", "Tipo", "Descripción", "Monto", "Fecha"])
        st.subheader("📌 Ingresos registrados hoy")
        st.dataframe(df_ing)
        total_dia = df_ing["Monto"].sum()
        st.success(f"💵 Total del día: ${total_dia:.2f}")
    else:
        st.info("No hay ingresos extraordinarios registrados hoy.")



# ---------------------------------------------------------
# 🟥 APLICACIÓN DE MULTAS
# ---------------------------------------------------------
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
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
    fecha_raw = st.date_input("📅 Fecha de aplicación")
    fecha = fecha_raw.strftime("%Y-%m-%d")
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

    st.subheader("🔎 Filtrar multas registradas")

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
        cols = st.columns([1, 3, 3, 2, 2, 2, 2])
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
                st.success(f"Estado actualizado para la multa ID {id_multa}")
                st.rerun()

    else:
        st.info("No hay multas registradas con esos filtros.")



# ---------------------------------------------------------
# 🟩 REGISTRO DE NUEVAS SOCIAS
# ---------------------------------------------------------
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de nuevas socias")

    con = obtener_conexion()
    if not con:
        st.error("No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    st.subheader("➕ Agregar una nueva socia")

    nombre = st.text_input("Nombre completo de la socia")

    if st.button("💾 Registrar socia"):

        if nombre.strip() == "":
            st.warning("⚠ Debe escribir un nombre.")
            return

        try:
            cursor.execute("""
                INSERT INTO Socia (Nombre, Sexo)
                VALUES (%s, 'F')
            """, (nombre,))

            con.commit()
            st.success(f"👩‍🦰 Nueva socia registrada correctamente: {nombre}")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar socia: {e}")

    st.markdown("---")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["ID", "Nombre"])
        st.dataframe(df)
    else:
        st.info("Aún no hay socias registradas.")



# ---------------------------------------------------------
# 📄 GENERAR REPORTE
# ---------------------------------------------------------
def pagina_reporte():

    st.header("📄 Reporte general del grupo")

    con = obtener_conexion()
    if not con:
        st.error("No se pudo conectar a la BD.")
        return

    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Seleccione la fecha del reporte", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    st.write("### Datos registrados")

    # Asistencia
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        JOIN Reunion R ON R.Id_Reunion = A.Id_Reunion
        WHERE R.Fecha_reunion = %s
    """, (fecha,))
    asistencia = cursor.fetchall()

    if asistencia:
        df_a = pd.DataFrame(asistencia, columns=["Socia", "Asistencia"])
        st.subheader("📝 Asistencia")
        st.dataframe(df_a)
    else:
        st.info("No hay datos de asistencia para esta fecha.")

    # Ingresos extraordinarios
    cursor.execute("""
        SELECT S.Nombre, I.Tipo, I.Descripcion, I.Monto
        FROM IngresosExtra I
        JOIN Socia S ON S.Id_Socia = I.Id_Socia
        JOIN Reunion R ON R.Id_Reunion = I.Id_Reunion
        WHERE R.Fecha_reunion = %s
    """, (fecha,))
    ingresos = cursor.fetchall()

    if ingresos:
        df_i = pd.DataFrame(ingresos, columns=["Socia", "Tipo", "Descripción", "Monto"])
        st.subheader("💰 Ingresos extraordinarios")
        st.dataframe(df_i)
        st.success(f"Total del día: ${df_i['Monto'].sum():.2f}")
    else:
        st.info("No hay ingresos extraordinarios para esta fecha.")

    st.markdown("---")
    st.subheader("📄 Exportar reporte a PDF")

    if st.button("⬇ Descargar PDF"):

        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            import io

        except ImportError:
            st.error("⚠ No se encontró la librería reportlab.")
            st.info("Agrega esto a tu requirements.txt:")
            st.code("reportlab")
            return

        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, 760, "Reporte General del Grupo")
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, 740, f"Fecha: {fecha}")

        y = 710
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "Asistencia:")
        y -= 20
        pdf.setFont("Helvetica", 12)

        if asistencia:
            for nombre, estado in asistencia:
                pdf.drawString(60, y, f"- {nombre}: {estado}")
                y -= 15
        else:
            pdf.drawString(60, y, "No hay registros.")
            y -= 20

        y -= 10
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(50, y, "Ingresos extraordinarios:")
        y -= 20
        pdf.setFont("Helvetica", 12)

        if ingresos:
            for fila in ingresos:
                nombre, tipo, desc, monto = fila
                pdf.drawString(60, y, f"- {nombre} | {tipo} | ${monto}")
                y -= 15
        else:
            pdf.drawString(60, y, "No hay registros.")

        pdf.save()
        buffer.seek(0)

        st.download_button(
            label="📥 Descargar reporte PDF",
            data=buffer,
            file_name=f"Reporte_{fecha}.pdf",
            mime="application/pdf"
        )
