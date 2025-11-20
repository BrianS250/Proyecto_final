# =======================
#   DIRECTIVA.PY COMPLETO
# =======================

import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro


# ============================================================
# PANEL PRINCIPAL
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    # ------------------------------------------------------
    # MOSTRAR SALDO DE CAJA
    # ------------------------------------------------------
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT Saldo_actual 
            FROM Caja 
            ORDER BY Id_Caja DESC LIMIT 1
        """)
        row = cursor.fetchone()

        saldo = row[0] if row else 0
        st.info(f"💰 Saldo actual de caja: **${saldo}**")

    except:
        st.warning("⚠ Error al obtener el saldo de Caja.")

    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    menu = st.sidebar.radio(
        "Selección rápida:",
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



# ============================================================
# ASISTENCIA + INGRESOS EXTRAORDINARIOS
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de la reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    # ---------------------------
    # CREAR REUNIÓN SI NO EXISTE
    # ---------------------------
    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion(Fecha_reunion, Observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES(%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.success(f"Reunión creada correctamente (ID {id_reunion}).")

    # ---------------------------
    # LISTA DE SOCIAS
    # ---------------------------
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

    if st.button("💾 Guardar asistencia"):
        for id_socia, asis in asistencia_registro.items():
            estado = "Presente" if asis == "SI" else "Ausente"

            cursor.execute("""
                SELECT Id_Asistencia
                FROM Asistencia
                WHERE Id_Reunion=%s AND Id_Socia=%s
            """, (id_reunion, id_socia))

            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE Asistencia SET Estado_asistencia=%s, Fecha=%s
                    WHERE Id_Reunion=%s AND Id_Socia=%s
                """, (estado, fecha, id_reunion, id_socia))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia(Id_Reunion,Id_Socia,Estado_asistencia,Fecha)
                    VALUES(%s,%s,%s,%s)
                """, (id_reunion, id_socia, estado, fecha))

        con.commit()
        st.success("Asistencia actualizada.")

    # ---------------------------
    # MOSTRAR REGISTRO
    # ---------------------------
    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia=A.Id_Socia
        WHERE A.Id_Reunion=%s
    """, (id_reunion,))
    registros = cursor.fetchall()

    if registros:
        df = pd.DataFrame(registros, columns=["Socia", "Asistencia"])
        st.dataframe(df)

        total_presentes = df[df.Asistencia == "Presente"].shape[0]
        st.success(f"Total presentes: {total_presentes}")

    st.markdown("---")

    # ============================================================
    # INGRESOS EXTRAORDINARIOS
    # ============================================================
    st.header("💰 Ingresos extraordinarios")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista_socias = cursor.fetchall()
    opc_socias = {nombre: id_s for id_s, nombre in lista_socias}

    socia_sel = st.selectbox("Socia que aporta:", opc_socias.keys())
    id_socia = opc_socias[socia_sel]

    tipo = st.selectbox("Tipo", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):

        cursor.execute("""
            INSERT INTO IngresosExtra(Id_Reunion,Id_Socia,Tipo,Descripcion,Monto,Fecha)
            VALUES(%s,%s,%s,%s,%s,%s)
        """, (id_reunion, id_socia, tipo, descripcion, monto, fecha))

        cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        row = cursor.fetchone()
        saldo_actual = row[0] if row else 0

        nuevo_saldo = saldo_actual + monto

        cursor.execute("""
            INSERT INTO Caja(Concepto,Monto,Saldo_actual,Id_Grupo,Id_Tipo_movimiento,Fecha)
            VALUES(%s,%s,%s,1,2,CURRENT_DATE())
        """, (f"Ingreso extraordinario – {socia_sel}", monto, nuevo_saldo))

        con.commit()
        st.success("Ingreso extraordinario registrado.")
        st.rerun()



# ============================================================
# MULTAS (CON FILTRO + ACTUALIZACIÓN + SUMA A CAJA)
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_s for id_s, nombre in socias}

    socia_sel = st.selectbox("Socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {nombre: id_t for id_t, nombre in tipos}

    tipo_sel = st.selectbox("Tipo:", lista_tipos.keys())
    id_tipo_multa = lista_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)
    fecha_raw = st.date_input("Fecha", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa(Monto,Fecha_aplicacion,Estado,Id_Tipo_multa,Id_Socia)
            VALUES(%s,%s,%s,%s,%s)
        """, (monto, fecha, estado, id_tipo_multa, id_socia))
        con.commit()
        st.success("Multa registrada.")
        st.rerun()

    st.markdown("---")
    st.subheader("🔎 Filtrar multas registradas")

    filtro_socia = st.selectbox("Por socia:", ["Todas"] + list(lista_socias.keys()))
    filtro_estado = st.selectbox("Por estado:", ["Todos", "A pagar", "Pagada"])
    filtro_fecha_raw = st.date_input("Por fecha:", value=None)
    filtro_fecha = filtro_fecha_raw.strftime("%Y-%m-%d") if filtro_fecha_raw else None

    query = """
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia=M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa=M.Id_Tipo_multa
        WHERE 1=1
    """
    params = []

    if filtro_socia != "Todas":
        query += " AND S.Nombre=%s"
        params.append(filtro_socia)

    if filtro_estado != "Todos":
        query += " AND M.Estado=%s"
        params.append(filtro_estado)

    if filtro_fecha:
        query += " AND M.Fecha_aplicacion=%s"
        params.append(filtro_fecha)

    query += " ORDER BY M.Id_Multa DESC"

    cursor.execute(query, params)
    multas = cursor.fetchall()

    st.subheader("📋 Multas registradas")

    for mid, socia, tipo, monto, estado_actual, fecha_m in multas:

        c1, c2, c3, c4, c5, c6, c7 = st.columns([1,3,3,2,2,2,2])

        c1.write(mid)
        c2.write(socia)
        c3.write(tipo)
        c4.write(f"${monto}")
        nuevo_estado = c5.selectbox(
            " ",
            ["A pagar", "Pagada"],
            index=0 if estado_actual == "A pagar" else 1,
            key=f"m_{mid}"
        )
        c6.write(str(fecha_m))

        if c7.button("Actualizar", key=f"u_{mid}"):

            # SUMAR A CAJA SOLO SI PASA DE A PAGAR → PAGADA
            if estado_actual == "A pagar" and nuevo_estado == "Pagada":

                cursor.execute("SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
                row = cursor.fetchone()
                saldo_actual = row[0] if row else 0

                nuevo_saldo = saldo_actual + monto

                cursor.execute("""
                    INSERT INTO Caja(Concepto,Monto,Saldo_actual,Id_Grupo,Id_Tipo_movimiento,Id_Multa,Fecha)
                    VALUES(%s,%s,%s,1,2,%s,CURRENT_DATE())
                """, (
                    f"Pago de multa – {socia}",
                    monto,
                    nuevo_saldo,
                    mid
                ))

            cursor.execute("UPDATE Multa SET Estado=%s WHERE Id_Multa=%s", (nuevo_estado, mid))
            con.commit()
            st.success(f"Multa {mid} actualizada.")
            st.rerun()



# ============================================================
# REGISTRO DE SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre completo")

    if st.button("Registrar socia"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        cursor.execute("INSERT INTO Socia(Nombre,Sexo) VALUES(%s,'F')", (nombre,))
        con.commit()
        st.success("Socia registrada.")
        st.rerun()

    cursor.execute("SELECT Id_Socia,Nombre FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["ID","Nombre"])
        st.dataframe(df)
