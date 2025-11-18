import streamlit as st
import pandas as pd
from modulos.conexion import obtener_conexion


# ============================================================
# 🔐 BOTÓN DE CERRAR SESIÓN
# ============================================================
def cerrar_sesion():
    st.sidebar.title("Menú")
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state["sesion_iniciada"] = False
        st.rerun()


# ============================================================
# 🟦 PÁGINA DE ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.subheader("📝 Registro de asistencia del grupo")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # 1) Seleccionar fecha
    fecha = st.date_input("📅 Fecha de la reunión")

    # 2) Ver si ya existe reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, acuerdos, Tema_central, Id_Grupo)
            VALUES (%s,'','','','1')
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.info(f"📌 Nueva reunión creada (ID {id_reunion})")

    # 3) Cargar socias
    cursor.execute("SELECT Id_Socia, Nombre, Sexo FROM Socia")
    datos = cursor.fetchall()
    socias = {fila[1]: fila for fila in datos}

    socia_sel = st.selectbox("👩 Seleccione la socia:", list(socias.keys()))
    id_socia = socias[socia_sel][0]
    genero = socias[socia_sel][2]

    st.text_input("Género:", genero, disabled=True)

    # 4) Estado
    estado = st.selectbox("📍 Estado asistencia:", ["Presente", "Ausente"])

    # 5) Guardar asistencia
    if st.button("💾 Guardar asistencia"):
        try:
            cursor.execute("""
                INSERT INTO Asistencia (Id_Reunion, Id_Socia, Estado_asistencia, Genero, Fecha)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_reunion, id_socia, estado, genero, fecha))

            con.commit()
            st.success("✅ Asistencia guardada")
        except Exception as e:
            st.error(f"⚠ Error: {e}")

    # 6) Mostrar tabla
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
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay asistencias registradas aún.")


# ============================================================
# 🟪 PÁGINA DE MULTAS
# ============================================================
def pagina_multas():

    st.subheader("⚠ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = con.cursor()

    # Socia
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    datos = cursor.fetchall()
    socias = {s[1]: s[0] for s in datos}

    socia_sel = st.selectbox("👩 Seleccione la socia:", list(socias.keys()))
    id_socia = socias[socia_sel]

    # Tipo de multa
    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos = cursor.fetchall()
    tipos_multa = {t[1]: t[0] for t in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", list(tipos_multa.keys()))
    id_tipo = tipos_multa[tipo_sel]

    fecha = st.date_input("📅 Fecha de aplicación")
    monto = st.number_input("💲 Monto de la multa", min_value=0.0, step=0.50)
    estado = st.selectbox("🔖 Estado:", ["A pagar", "Pagada"])

    # Guardar multa
    if st.button("💾 Guardar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """, (monto, fecha, estado, id_tipo, id_socia))

            con.commit()
            st.success("✅ Multa registrada correctamente.")
        except Exception as e:
            st.error(f"⚠ Error: {e}")

    # Mostrar multas
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.Tipo_de_multa, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN Tipo_de_multa T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["ID", "Socia", "Tipo", "Monto", "Estado", "Fecha"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay multas registradas aún.")


# ============================================================
# 🟩 PANEL PRINCIPAL — DOS SECCIONES LATERALES
# ============================================================
def interfaz_directiva():

    cerrar_sesion()

    st.title("👩‍⚖️ Panel de la Directiva del Grupo")
    st.write("Administre reuniones, asistencia, préstamos y multas.")

    menu = st.sidebar.radio(
        "📌 Seleccione una opción:",
        ["Registro de asistencia", "Aplicar multas"]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Aplicar multas":
        pagina_multas()
