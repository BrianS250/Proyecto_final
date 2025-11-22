import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.reporte_caja import reporte_caja

# CAJA POR REUNIÓN
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha

# OTROS GASTOS
from modulos.gastos_grupo import gastos_grupo

# CIERRE DE CICLO
from modulos.cierre_ciclo import cierre_ciclo

# REGLAS INTERNAS
from modulos.reglas import gestionar_reglas



# ============================================================
# PANEL PRINCIPAL — DIRECTIVA
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de la Directiva del Grupo")

    st.markdown("### 📅 Seleccione la fecha de reunión del reporte:")

    if "fecha_global" not in st.session_state:
        st.session_state["fecha_global"] = date.today().strftime("%Y-%m-%d")

    fecha_sel = st.date_input(
        "Fecha del reporte",
        value=pd.to_datetime(st.session_state["fecha_global"])
    ).strftime("%Y-%m-%d")

    st.session_state["fecha_global"] = fecha_sel

    try:
        saldo = obtener_saldo_por_fecha(fecha_sel)
        st.info(f"💰 Saldo de caja para {fecha_sel}: **${saldo:.2f}**")
    except:
        st.warning("⚠ Error al obtener el saldo de caja.")

    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # -------------------------
    # MENÚ COMPLETO
    # -------------------------
    menu = st.sidebar.radio(
        "Selección rápida:",
        [
            "Registro de asistencia",
            "Aplicar multas",
            "Registrar nuevas socias",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Registrar ahorro",
            "Registrar otros gastos",
            "Filtrar multas",      # ← NUEVA OPCIÓN
            "Cierre de ciclo",
            "Reporte de caja",
            "Reglas internas"
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
    elif menu == "Registrar otros gastos":
        gastos_grupo()
    elif menu == "Filtrar multas":
        pagina_filtrar_multas()
    elif menu == "Cierre de ciclo":
        cierre_ciclo()
    elif menu == "Reporte de caja":
        reporte_caja()
    elif menu == "Reglas internas":
        gestionar_reglas()



def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # 1️⃣ REGISTRAR UNA MULTA
    # ============================================================

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre ASC")
    socias = cursor.fetchall()
    opciones_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    st.subheader("➕ Registrar nueva multa")

    socia_sel = st.selectbox("Socia:", opciones_socias.keys())
    id_socia = opciones_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    opciones_tipos = {t["Tipo de multa"]: t["Id_Tipo_multa"] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", opciones_tipos.keys())
    id_tipo = opciones_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.25, step=0.25)

    fecha_raw = st.date_input("Fecha de aplicación", date.today())
    fecha_aplicacion = fecha_raw.strftime("%Y-%m-%d")

    estado_sel = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, %s, %s)
        """, (monto, fecha_aplicacion, estado_sel, id_tipo, id_socia))
        con.commit()

        st.success("✔ Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")

    # ============================================================
    # 2️⃣ FILTROS
    # ============================================================

    st.subheader("🔎 Filtrar multas")

    # FILTRO FECHA
    fecha_filtro = st.date_input("Filtrar por fecha (opcional)", value=None)
    fecha_sql = fecha_filtro.strftime("%Y-%m-%d") if fecha_filtro else None

    # FILTRO SOCIA
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre ASC")
    socias = cursor.fetchall()
    opciones_socias_f = {"Todas": None}
    for s in socias:
        opciones_socias_f[s["Nombre"]] = s["Id_Socia"]

    socia_filtrar = st.selectbox("Filtrar por socia:", opciones_socias_f.keys())
    id_socia_filtrar = opciones_socias_f[socia_filtrar]

    # FILTRO TIPO DE MULTA
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    opciones_tipo_f = {"Todos": None}
    for t in tipos:
        opciones_tipo_f[t["Tipo de multa"]] = t["Id_Tipo_multa"]

    tipo_filtro = st.selectbox("Filtrar por tipo:", opciones_tipo_f.keys())
    tipo_id_filtro = opciones_tipo_f[tipo_filtro]

    # FILTRO ESTADO
    estado_filtro = st.selectbox("Filtrar por estado:", ["Todos", "A pagar", "Pagada"])

    # ============================================================
    # 3️⃣ TABLA DE RESULTADOS FILTRADOS
    # ============================================================

    query = """
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa` AS Tipo,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1=1
    """
    params = []

    if fecha_sql:
        query += " AND M.Fecha_aplicacion = %s"
        params.append(fecha_sql)

    if id_socia_filtrar:
        query += " AND M.Id_Socia = %s"
        params.append(id_socia_filtrar)

    if tipo_id_filtro:
        query += " AND M.Id_Tipo_multa = %s"
        params.append(tipo_id_filtro)

    if estado_filtro != "Todos":
        query += " AND M.Estado = %s"
        params.append(estado_filtro)

    query += " ORDER BY M.Id_Multa DESC"

    cursor.execute(query, tuple(params))
    multas_filtradas = cursor.fetchall()

    st.subheader("📋 Resultados filtrados")

    if not multas_filtradas:
        st.info("No hay multas que coincidan con los filtros.")
    else:
        df = pd.DataFrame(multas_filtradas)
        st.dataframe(df, hide_index=True)

    st.markdown("---")

    # ============================================================
    # 4️⃣ MULTAS PENDIENTES (Al final)
    # ============================================================

    st.subheader("📌 Multas pendientes (A pagar)")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa` AS Tipo,
               M.Monto, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia=M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE M.Estado='A pagar'
        ORDER BY M.Id_Multa DESC
    """)
    pendientes = cursor.fetchall()

    if not pendientes:
        st.info("No hay multas pendientes.")
    else:
        for multa in pendientes:

            col1, col2, col3, col4, col5 = st.columns([1, 3, 3, 2, 3])

            col1.write(multa["Id_Multa"])
            col2.write(multa["Nombre"])
            col3.write(multa["Tipo"])
            col4.write(f"${multa['Monto']}")

            if col5.button("Marcar como pagada", key=f"paga_{multa['Id_Multa']}"):

                id_caja = obtener_o_crear_reunion(multa["Fecha_aplicacion"])
                registrar_movimiento(
                    id_caja,
                    "Ingreso",
                    f"Pago de multa – {multa['Nombre']}",
                    float(multa["Monto"])
                )

                cursor.execute(
                    "UPDATE Multa SET Estado='Pagada' WHERE Id_Multa=%s",
                    (multa["Id_Multa"],)
                )
                con.commit()

                st.success("✔ Multa marcada como pagada.")
                st.rerun()

    cursor.close()
    con.close()


# ============================================================
# ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("📅 Fecha de la reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row[0]
    else:
        cursor.execute("""
            INSERT INTO Reunion(Fecha_reunion, Observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES(%s,'','','',1)
        """, (fecha,))
        con.commit()
        id_reunion = cursor.lastrowid
        st.success(f"Reunión creada (ID {id_reunion}).")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")
    registro = {}

    for id_socia, nombre in socias:
        estado = st.selectbox(
            f"{id_socia} - {nombre}",
            ["SI", "NO"],
            key=f"asis_{id_socia}"
        )
        registro[id_socia] = estado

    if st.button("💾 Guardar asistencia"):
        for id_socia, valor in registro.items():
            est = "Presente" if valor == "SI" else "Ausente"

            cursor.execute("""
                SELECT Id_Asistencia FROM Asistencia
                WHERE Id_Reunion=%s AND Id_Socia=%s
            """, (id_reunion, id_socia))
            existe = cursor.fetchone()

            if existe:
                cursor.execute("""
                    UPDATE Asistencia
                    SET Estado_asistencia=%s, Fecha=%s
                    WHERE Id_Reunion=%s AND Id_Socia=%s
                """, (est, fecha, id_reunion, id_socia))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia(Id_Reunion,Id_Socia,Estado_asistencia,Fecha)
                    VALUES(%s,%s,%s,%s)
                """, (id_reunion, id_socia, est, fecha))

        con.commit()
        st.success("Asistencia registrada.")

    cursor.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia=A.Id_Socia
        WHERE A.Id_Reunion=%s
    """, (id_reunion,))
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["Socia", "Asistencia"])
        st.dataframe(df)

        total_socias = len(datos)
        presentes = sum(1 for _, est in datos if est == "Presente")
        ausentes = total_socias - presentes

        st.markdown("### 📊 Resumen de asistencia")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de socias", total_socias)
        c2.metric("Presentes", presentes)
        c3.metric("Ausentes", ausentes)

    st.markdown("---")

    # INGRESOS EXTRAORDINARIOS
    st.header("💰 Ingresos extraordinarios")

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    opciones = {nombre: id_s for id_s, nombre in socias}

    socia_sel = st.selectbox("Socia:", opciones.keys())
    id_socia = opciones[socia_sel]

    tipo = st.selectbox("Tipo", ["Rifa", "Donación", "Actividad", "Otro"])
    descripcion = st.text_input("Descripción")
    monto = st.number_input("Monto ($)", min_value=0.25, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):
        cursor.execute("""
            INSERT INTO IngresosExtra(Id_Reunion,Id_Socia,Tipo,Descripcion,Monto,Fecha)
            VALUES(%s,%s,%s,%s,%s,%s)
        """, (id_reunion, id_socia, tipo, descripcion, monto, fecha))

        con.commit()

        id_caja = obtener_o_crear_reunion(fecha)
        registrar_movimiento(id_caja, "Ingreso", f"Ingreso Extra – {tipo}", monto)

        st.success("Ingreso extraordinario registrado y sumado a caja.")
        st.rerun()




# ============================================================
# MULTAS — SOLO APLICACIÓN
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    opciones = {nombre: id_s for id_s, nombre in socias}

    socia_sel = st.selectbox("Socia:", opciones.keys())
    id_socia = opciones[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa`")
    tipos = cursor.fetchall()
    lista_tipos = {nombre: id_t for id_t, nombre in tipos}

    tipo_sel = st.selectbox("Tipo:", lista_tipos.keys())
    id_tipo = lista_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.25, step=0.25)
    fecha_raw = st.date_input("Fecha", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa(Monto,Fecha_aplicacion,Estado,Id_Tipo_multa,Id_Socia)
            VALUES(%s,%s,%s,%s,%s)
        """, (monto, fecha, estado, id_tipo, id_socia))

        con.commit()
        st.success("Multa registrada.")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Multas pendientes")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia=M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE M.Estado='A pagar'
        ORDER BY M.Id_Multa DESC
    """)
    multas = cursor.fetchall()

    for mid, nombre, tipo, monto, estado_actual, fecha_m in multas:

        c1, c2, c3, c4, c5 = st.columns([1,3,3,2,3])

        c1.write(mid)
        c2.write(nombre)
        c3.write(tipo)
        c4.write(f"${monto}")

        if c5.button("Marcar como pagada", key=f"btn{mid}"):

            id_caja = obtener_o_crear_reunion(fecha_m)
            registrar_movimiento(
                id_caja,
                "Ingreso",
                f"Pago de multa – {nombre}",
                monto
            )

            cursor.execute("UPDATE Multa SET Estado='Pagada' WHERE Id_Multa=%s", (mid,))
            con.commit()

            st.success(f"Multa {mid} pagada.")
            st.rerun()




# ============================================================
# REGISTRO DE SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor()

    nombre = st.text_input("Nombre completo")
    dui_raw = st.text_input("DUI (9 dígitos, sin guion)", max_chars=9)

    dui_formateado = ""
    if dui_raw.isdigit() and len(dui_raw) == 9:
        dui_formateado = f"{dui_raw[:8]}-{dui_raw[8]}"
        st.success(f"Formato DUI: {dui_formateado}")
    else:
        st.info("Formato DUI esperado: 00000000-0")

    telefono_raw = st.text_input("Teléfono (8 dígitos)", max_chars=8)

    if telefono_raw and not telefono_raw.isdigit():
        st.error("El teléfono solo debe contener números.")

    if st.button("Registrar socia"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        if not (dui_raw.isdigit() and len(dui_raw) == 9):
            st.error("El DUI debe contener exactamente 9 dígitos.")
            return

        if not (telefono_raw.isdigit() and len(telefono_raw) == 8):
            st.error("El teléfono debe contener exactamente 8 dígitos.")
            return

        cursor.execute("""
            INSERT INTO Socia(Nombre, DUI, Telefono, Sexo)
            VALUES(%s, %s, %s, 'F')
        """, (nombre, dui_formateado, telefono_raw))

        con.commit()

        st.success("Socia registrada correctamente.")
        st.rerun()

    cursor.execute("SELECT Id_Socia AS ID, Nombre, DUI, Telefono FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["ID", "Nombre", "DUI", "Teléfono"])
        st.dataframe(df, hide_index=True)

    cursor.close()
    con.close()
