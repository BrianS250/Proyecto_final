import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion


# =============================================================================
#                           PANEL PRINCIPAL DE DIRECTIVA
# =============================================================================
def interfaz_directiva():
    st.title("👔 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, préstamos y multas.")

    # Botón para cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.rerun()

    # Menú de opciones
    st.subheader("📌 Seleccione una opción:")
    opcion = st.selectbox(
        "",
        ["Registro de asistencia", "Aplicar multas"]  # <<<<<<<< CORREGIDO
    )

    if opcion == "Registro de asistencia":
        pagina_asistencia()

    elif opcion == "Aplicar multas":
        pagina_multas()


# =============================================================================
#                                ASISTENCIA
# =============================================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # FECHA
    fecha = st.date_input("📅 Fecha de la reunión")

    # Verificar si ya existe reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        cursor.execute(
            "INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo) "
            "VALUES (%s,'','','','1')",
            (fecha,)
        )
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Nueva reunión creada automáticamente con ID: {id_reunion}")

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    socias = cursor.fetchall()

    lista_socias = {s[1]: (s[0], s[2]) for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())

    id_socia = lista_socias[socia_sel][0]
    genero = lista_socias[socia_sel][1]

    st.text_input("Género:", genero, disabled=True)

    # ESTADO ASISTENCIA
    estado = st.selectbox("📍 Estado asistencia:", ["Presente", "Ausente"])

    # GUARDAR
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero, fecha))
            con.commit()
            st.success("✅ Asistencia registrada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"⚠ Error al guardar asistencia: {e}")

    # MOSTRAR ASISTENCIA
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


# =============================================================================
#                                 MULTAS
# =============================================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {s[1]: s[0] for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # TIPOS DE MULTA (CORREGIDO)
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_multa")
    tipos = cursor.fetchall()
    tipos_multa = {t[1]: t[0] for t in tipos}

    tipo_sel = st.selectbox("📝 Tipo de multa:", tipos_multa.keys())
    id_tipo_multa = tipos_multa[tipo_sel]

    # MONTO
    monto = st.number_input("💵 Monto:", min_value=0.0, step=0.5)

    # FECHA
    fecha = st.date_input("📅 Fecha de aplicación")

    # GUARDAR MULTA
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, "A pagar", id_tipo_multa, id_socia))
            con.commit()
            st.success("✅ Multa registrada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"⚠ Error al guardar la multa: {e}")

    # LISTADO DE MULTAS
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.Tipo_de_multa, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN Tipo_multa T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)

    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(multas, columns=["ID", "Socia", "Tipo", "Monto", "Estado", "Fecha"])
        st.dataframe(df)
    else:
        st.info("No hay multas registradas aún.")
