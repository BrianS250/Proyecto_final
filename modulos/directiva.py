import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 PANEL PRINCIPAL (Título dinámico según el rol)
# ---------------------------------------------------------
def interfaz_directiva():

    rol = st.session_state.get("rol", "").lower()

    # -----------------------------------------------------
    # TÍTULO SEGÚN EL ROL
    # -----------------------------------------------------
    if rol == "director":
        st.title("👩‍💼 Panel de la Directiva del Grupo")
        st.write("Administre reuniones, asistencia y multas.")
    elif rol == "admin":
        st.title("🧑‍💼 Panel del Administrador")
        st.write("Gestione funciones generales del sistema.")
    else:  # promotora
        st.title("👩‍🧾 Panel de la Promotora")
        st.write("Acceso a consultas y funciones limitadas.")

    # Botón cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # -----------------------------------------------------
    # SOLO EL DIRECTOR PUEDE VER EL MENÚ COMPLETO
    # -----------------------------------------------------
    if rol != "director":
        st.info("Puedes usar otras funciones del sistema, pero esta sección no está disponible para tu rol.")
        return

    # Menú exclusivo del Director
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
    if not con:
        st.error("No se pudo conectar a la BD.")
        return

    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Verificar si existe reunión
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
            st.error("⚠ ERROR: No se pudo crear la reunión. Revise que Id_Grupo exista.")
            return

    # Obtener socias
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

    # Guardar
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
# 🟥 MULTAS  (solo Director)
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
