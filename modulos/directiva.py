import streamlit as st
from modulos.Configuracion.conexion import obtener_conexion
import pandas as pd
from datetime import date

# -------------------------------------------------------------------
# MENÚ PRINCIPAL DE LA DIRECTIVA
# -------------------------------------------------------------------

def interfaz_directiva():
    st.title("🧑‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia y multas del grupo.")

    opcion = st.sidebar.radio(
        "Seleccione una sección:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if opcion == "Registro de asistencia":
        pagina_asistencia()

    elif opcion == "Aplicar multas":
        pagina_multas()

# -------------------------------------------------------------------
# PÁGINA: REGISTRO DE ASISTENCIA
# -------------------------------------------------------------------

def pagina_asistencia():

    st.subheader("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("Error al conectar con la base de datos.")
        return
    cursor = con.cursor()

    # Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("No hay socias registradas.")
        return

    lista_nombres = [s[1] for s in socias]
    seleccion = st.selectbox("👩 Seleccione la socia:", lista_nombres)

    # Recuperar datos de la socia seleccionada
    socia = next(s for s in socias if s[1] == seleccion)
    id_socia = socia[0]
    genero = socia[2]

    st.text_input("Género:", genero)

    # Fecha de asistencia
    fecha_asistencia = st.date_input("📅 Fecha de la reunión:", date.today())

    estado = st.selectbox("📌 Estado asistencia:", ["Presente", "Ausente"])

    # Guardar asistencia
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Fecha, Estado, Id_Socia)
                VALUES (%s, %s, %s)
            """, (fecha_asistencia, estado, id_socia))
            con.commit()
            st.success("Asistencia guardada correctamente.")
        except Exception as e:
            st.error(f"Error al guardar asistencia: {e}")

    st.divider()
    st.subheader("📋 Asistencias registradas")

    cursor.execute("""
        SELECT A.Id_Asistencia, S.Nombre, A.Fecha, A.Estado
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        ORDER BY A.Id_Asistencia DESC
    """)
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Fecha", "Estado"])
        st.dataframe(df)
    else:
        st.info("Aún no hay asistencias registradas.")


# -------------------------------------------------------------------
# PÁGINA: APLICAR MULTAS
# -------------------------------------------------------------------

def pagina_multas():

    st.subheader("⚠ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("Error al conectar con la base de datos.")
        return
    cursor = con.cursor()

    # Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {s[1]: s[0] for s in socias}

    seleccion_socia = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[seleccion_socia]

    # Cargar tipos de multa
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {t[1]: t[0] for t in tipos}

    seleccion_tipo = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[seleccion_tipo]

    # Monto de multa
    monto = st.number_input("💲 Monto de la multa:", step=0.50, min_value=0.0)

    # Fecha de aplicación
    fecha_aplicacion = st.date_input("📅 Fecha de aplicación:", date.today())

    estado = "A pagar"

    if st.button("💾 Guardar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha_aplicacion, estado, id_tipo_multa, id_socia))

            con.commit()
            st.success("Multa registrada correctamente.")
        except Exception as e:
            st.error(f"Error al guardar multa: {e}")

    # Mostrar multas registradas
    st.divider()
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)
    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(multas, columns=["ID", "Socia", "Tipo", "Monto", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("Aún no hay multas registradas.")
