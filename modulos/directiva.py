import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro


# ---------------------------------------------------------
# PANEL PRINCIPAL DIRECTIVA
# ---------------------------------------------------------
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso al sistema")
        st.warning("⚠️ Acceso restringido. Esta sección es exclusiva para el Director.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # Mostrar saldo de caja
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        row = cursor.fetchone()

        if row:
            st.info(f"💰 Saldo actual de caja: **${row[0]}**")
        else:
            st.warning("⚠ Caja aún no tiene movimientos.")
    except:
        st.warning("⚠ No se pudo obtener el saldo de caja.")

    # Cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Menú principal
    menu = st.sidebar.radio(
        "Seleccione una sección:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro"
        ]
    )

    if menu == "Registro de asistencia":
        pagina_asistencia()
    elif menu == "Aplicar multas":
        pagina_multas()
    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()
    elif menu == "Autorizar préstamo":
        autorizar_prestamo()
    elif menu == "Registrar pago de préstamo":
        pago_prestamo()
    elif menu == "Registrar ahorro":
        ahorro()



# ---------------------------------------------------------
# 🟩 REGISTRO DE ASISTENCIA + INGRESOS EXTRAORDINARIOS
# ---------------------------------------------------------
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de reunión", value=date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Buscar o crear reunión
    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion = %s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES (%s, '', '', '', 1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid

    # Listado de socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")
    asistencia_registro = {}

    for id_socia, nombre in socias:
        asistencia = st.selectbox(
            f"{id_socia} - {nombre}",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )
        asistencia_registro[id_socia] = asistencia

    # Guardar asistencia
    if st.button("💾 Guardar asistencia general"):

        for id_socia, asistencia in asistencia_registro.items():
            estado = "Presente" if asistencia == "SI" else "Ausente"

            cursor.execute("""
                SELECT Id_Asistencia FROM Asistencia 
                WHERE Id_Reunion = %s AND Id_Socia = %s
            """, (id_reunion, id_socia))

            existe = cursor.fetchone()

            if existe:
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
        st.rerun()

    # Mostrar asistencia del día
    cursor.execute("""
        SELECT S.Id_Socia, S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON A.Id_Socia = S.Id_Socia
        WHERE A.Id_Reunion = %s
    """, (id_reunion,))
    datos = cursor.fetchall()

    if datos:
        st.dataframe(pd.DataFrame(datos, columns=["ID", "Socia", "Asistencia"]))

    st.markdown("---")

    # -------------------------------
    # INGRESOS EXTRAORDINARIOS
    # -------------------------------
    st.header("💰 Ingresos extraordinarios")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista = cursor.fetchall()
    dict_socias = {f"{i} - {n}": i for i, n in lista}

    socia_sel = st.selectbox("👩 Socia que aporta:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    tipo = st.selectbox("Tipo de ingreso:", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto recibido ($):", min_value=0.50, step=0.50)

    if st.button("➕ Registrar ingreso extraordinario"):

        # Insertar en IngresosExtra
        cursor.execute("""
            INSERT INTO IngresosExtra (Id_Reunion, Id_Socia, Tipo, Descripcion, Monto, Fecha)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_reunion, id_socia, tipo, descripcion, monto, fecha))

        # Tomar saldo actual
        cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        row = cursor.fetchone()
        saldo_actual = row[0] if row else 0

        nuevo_saldo = saldo_actual + float(monto)

        # Insertar en Caja
        cursor.execute("""
            INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
            VALUES (%s, %s, %s, 1, 2, CURRENT_DATE())
        """, (f"Ingreso extraordinario – {socia_sel}", monto, nuevo_saldo))

        con.commit()
        st.success("Ingreso registrado y agregado a CAJA.")
        st.rerun()



# ---------------------------------------------------------
# 🟥 MULTAS (REGISTRO + PAGO)
# ---------------------------------------------------------
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    # Socias
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista = cursor.fetchall()
    dict_socias = {f"{i} - {n}": i for i, n in lista}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # Tipo de multa
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    dict_tipos = {n: i for i, n in tipos}

    tipo_sel = st.selectbox("📌 Tipo de multa:", dict_tipos.keys())
    id_tipo = dict_tipos[tipo_sel]

    monto = st.number_input("Monto ($):", min_value=0.50, step=0.50)
    fecha_raw = st.date_input("Fecha:")
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado_sel = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):

        cursor.execute("""
            INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, %s, %s)
        """, (monto, fecha, estado_sel, id_tipo, id_socia))

        con.commit()
        st.success("Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")
    st.subheader("🔍 Buscar y actualizar multas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        ORDER BY M.Id_Multa DESC
    """)
    multas = cursor.fetchall()

    if multas:
        df = pd.DataFrame(multas, columns=["ID", "Socia", "Monto", "Estado", "Fecha"])
        st.dataframe(df)

    lista_ids = [m[0] for m in multas]

    if lista_ids:
        id_multa_sel = st.selectbox("Seleccione multa para actualizar:", lista_ids)

        nuevo_estado = st.selectbox("Nuevo estado:", ["A pagar", "Pagada"])

        if st.button("Actualizar estado"):

            # Tomar monto
            cursor.execute("SELECT Monto FROM Multa WHERE Id_Multa = %s", (id_multa_sel,))
            monto = cursor.fetchone()[0]

            if nuevo_estado == "Pagada":

                cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
                row = cursor.fetchone()
                saldo = row[0] if row else 0

                nuevo_saldo = saldo + monto

                cursor.execute("""
                    INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha, Id_Multa)
                    VALUES (%s, %s, %s, 1, 2, CURRENT_DATE(), %s)
                """, (f"Pago de multa – ID {id_multa_sel}", monto, nuevo_saldo, id_multa_sel))

            cursor.execute("""
                UPDATE Multa 
                SET Estado = %s 
                WHERE Id_Multa = %s
            """, (nuevo_estado, id_multa_sel))

            con.commit()
            st.success("Estado actualizado correctamente.")
            st.rerun()



# ---------------------------------------------------------
# 🟩 REGISTRO DE SOCIAS
# ---------------------------------------------------------
def pagina_registro_socias():

    st.header("👩‍🦰 Registrar nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre completo")

    if st.button("💾 Registrar socia"):
        if nombre.strip() == "":
            st.warning("Escribe un nombre.")
        else:
            cursor.execute("""
                INSERT INTO Socia (Nombre, Sexo)
                VALUES (%s, 'F')
            """, (nombre,))
            con.commit()
            st.success("Socia registrada.")
            st.rerun()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["ID", "Nombre"]))
