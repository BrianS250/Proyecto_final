import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion



# ============================================================
# 🔐 BOTÓN DE CERRAR SESIÓN SIEMPRE DISPONIBLE
# ============================================================
def mostrar_boton_cerrar_sesion():
    if "sesion_iniciada" in st.session_state and st.session_state["sesion_iniciada"]:
        if st.sidebar.button("🔓 Cerrar sesión"):
            st.session_state["sesion_iniciada"] = False
            st.rerun()


# ============================================================
# 🧾 PÁGINA DE ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.subheader("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # 1️⃣ Fecha seleccionada
    fecha = st.date_input("📅 Fecha de la reunión")

    # 2️⃣ Buscar si ya existe reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        # Crear reunión automática
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s, '', '', '', 1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Nueva reunión creada (ID: {id_reunion})")

    # 3️⃣ Lista de socias
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    socias = cursor.fetchall()

    lista_socias = {s[1]: (s[0], s[2]) for s in socias}
    seleccion_socia = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())

    id_socia = lista_socias[seleccion_socia][0]
    genero_socia = lista_socias[seleccion_socia][2]

    # 4️⃣ Mostrar género autocompletado
    st.text_input("Género:", genero_socia, disabled=True)

    # 5️⃣ Estado asistencia
    estado = st.selectbox("📍 Estado asistencia:", ["Presente", "Ausente"])

    # 6️⃣ Guardar asistencia
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero_socia, fecha))
            con.commit()
            st.success("✅ Asistencia registrada.")
        except Exception as e:
            st.error(f"⚠ Error al guardar asistencia: {e}")

    # 7️⃣ Mostrar registros
    st.divider()
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


# ============================================================
# ⚠️ PÁGINA DE MULTAS
# ============================================================
def pagina_multas():

    st.subheader("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # Socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()
    lista_socias = {s[1]: s[0] for s in socias}
    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # Tipos de multa
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos = cursor.fetchall()
    lista_tipos = {t[1]: t[0] for t in tipos}
    tipo_sel = st.selectbox("📌 Tipo de multa:", lista_tipos.keys())
    id_tipo = lista_tipos[tipo_sel]

    monto = st.number_input("💲 Monto", min_value=0.00, step=0.50)
    fecha = st.date_input("📅 Fecha")

    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, 'A pagar', %s, %s)
            """, (monto, fecha, id_tipo, id_socia))

            con.commit()
            st.success("✅ Multa registrada.")
        except Exception as e:
            st.error(f"⚠ Error: {e}")

    # Mostrar multas aplicadas
    st.divider()
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.Tipo_de_multa, M.Monto, M.Fecha_aplicacion, M.Estado
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN Tipo_de_multa T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)
    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(multas, columns=["ID", "Socia", "Tipo", "Monto", "Fecha", "Estado"])
        st.dataframe(df)
    else:
        st.info("No hay multas registradas.")


# ============================================================
# 🧭 MENÚ PRINCIPAL DE DIRECTIVA
# ============================================================
def interfaz_directiva():

    mostrar_boton_cerrar_sesion()

    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, préstamos y multas.")

    menu = st.selectbox("📌 Seleccione una opción:", [
        "Registro de asistencia",
        "Aplicación de multas"
    ])

    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Aplicación de multas":
        pagina_multas()
