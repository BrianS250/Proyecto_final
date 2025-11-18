import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion


# --------------------------------------------------------------------
# PANEL PRINCIPAL
# --------------------------------------------------------------------
def interfaz_directiva():

    st.title("👨‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, préstamos y multas.")

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.experimental_rerun()

    opcion = st.selectbox(
        "📌 Seleccione una opción:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if opcion == "Registro de asistencia":
        pagina_asistencia()
    else:
        pagina_multas()



# --------------------------------------------------------------------
# REGISTRO DE ASISTENCIA
# --------------------------------------------------------------------
def pagina_asistencia():

    st.subheader("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar con la base de datos.")
        return

    cursor = con.cursor()

    # FECHA DE REUNIÓN
    fecha = st.date_input("📅 Fecha de la reunión")

    # Buscar si ya existe reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s,'','','','1')
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Reunión creada automáticamente con ID {id_reunion}")

    # LISTA DE SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    datos_socias = cursor.fetchall()

    socias = {fila[1]: (fila[0], fila[2]) for fila in datos_socias}
    nombre_socia = st.selectbox("👩 Seleccione la socia:", list(socias.keys()))

    id_socia = socias[nombre_socia][0]
    genero = socias[nombre_socia][2]

    st.text_input("Género:", genero, disabled=True)

    # ESTADO DE ASISTENCIA
    estado = st.selectbox("📍 Estado de asistencia:", ["Presente", "Ausente"])

    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero, fecha))
            con.commit()
            st.success("✅ Asistencia registrada correctamente.")
        except Exception as e:
            st.error(f"⚠️ Error al guardar: {e}")

    # MOSTRAR ASISTENCIAS
    st.subheader("📋 Asistencias registradas")

    cursor.execute("""
        SELECT A.Id_Asistencia, S.Nombre, A.Genero, A.Estado_asistencia, A.Fecha
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))

    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Género", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay asistencias registradas aún.")



# --------------------------------------------------------------------
# REGISTRO DE MULTAS
# --------------------------------------------------------------------
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar con la base de datos.")
        return

    cursor = con.cursor()

    # LISTA DE SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    datos_socias = cursor.fetchall()
    socias = {fila[1]: fila[0] for fila in datos_socias}

    nombre_socia = st.selectbox("👩 Seleccione una socia:", list(socias.keys()))
    id_socia = socias[nombre_socia]

    # LISTA DE TIPOS DE MULTA  (TU TABLA SE LLAMA EXACTAMENTE: `Tipo de multa`)
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()

    dict_tipo_multa = {fila[1]: fila[0] for fila in tipos}

    nombre_tipo = st.selectbox("📌 Tipo de multa:", list(dict_tipo_multa.keys()))
    id_tipo_multa = dict_tipo_multa[nombre_tipo]

    monto = st.number_input("💵 Monto:", min_value=1.0)
    fecha = st.date_input("📅 Fecha de aplicación")

    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, 'A pagar', %s, %s)
            """, (monto, fecha, id_tipo_multa, id_socia))
            con.commit()
            st.success("✅ Multa registrada correctamente.")
        except Exception as e:
            st.error(f"⚠️ Error al registrar multa: {e}")

    # MOSTRAR MULTAS
    st.subheader("📋 Multas registradas para esta socia")

    cursor.execute("""
        SELECT M.Id_Multa, T.`Tipo de multa`, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE M.Id_Socia = %s
    """, (id_socia,))

    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(multas, columns=["ID", "Tipo", "Monto", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay multas registradas para esta socia.")
