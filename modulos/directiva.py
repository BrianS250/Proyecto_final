import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.reporte_caja import reporte_caja

# CAJA (ACTUALIZADO A CAJA ÚNICA)
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_actual

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

    # Fecha global
    if "fecha_global" not in st.session_state:
        st.session_state["fecha_global"] = date.today().strftime("%Y-%m-%d")

    fecha_sel = st.date_input(
        "📅 Fecha del reporte",
        value=pd.to_datetime(st.session_state["fecha_global"])
    ).strftime("%Y-%m-%d")

    st.session_state["fecha_global"] = fecha_sel

    # SALDO REAL DE CAJA (YA NO POR FECHA)
    try:
        saldo = obtener_saldo_actual()
        st.info(f"💰 Saldo real en caja: **${saldo:.2f}**")
    except:
        st.warning("⚠ Error al obtener el saldo de caja.")

    # Cerrar sesión
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # Menú lateral
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
    elif menu == "Cierre de ciclo":
        cierre_ciclo()
    elif menu == "Reporte de caja":
        reporte_caja()
    elif menu == "Reglas internas":
        gestionar_reglas()



# ============================================================
# MULTAS — REGISTRO + FILTROS + PENDIENTES
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # SOCIAS
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    opciones_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # TIPOS DE MULTA
    cursor.execute("SELECT Id_Tipo_multa, `Tipo de multa` FROM `Tipo de multa` ORDER BY Id_Tipo_multa ASC")
    tipos = cursor.fetchall()

    opciones_tipos = {t["Tipo de multa"]: t["Id_Tipo_multa"] for t in tipos}

    # --------------------------
    # REGISTRAR MULTA
    # --------------------------
    st.subheader("➕ Registrar nueva multa")

    socia_sel = st.selectbox("Socia:", opciones_socias.keys())
    id_socia = opciones_socias[socia_sel]

    tipo_sel = st.selectbox("Tipo de multa:", opciones_tipos.keys())
    id_tipo = opciones_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.25, step=0.25)
    fecha = st.date_input("Fecha", date.today()).strftime("%Y-%m-%d")
    estado_sel = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):
        cursor.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s,%s,%s,%s,%s)
        """, (monto, fecha, estado_sel, id_tipo, id_socia))
        con.commit()
        st.success("✔ Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")

    # --------------------------
    # FILTROS
    # --------------------------
    st.subheader("🔎 Filtrar multas")

    fecha_filtro = st.date_input("Fecha (opcional)", value=None)
    fecha_sql = fecha_filtro.strftime("%Y-%m-%d") if fecha_filtro else None

    opciones_socias_f = {"Todas": None}
    for s in socias:
        opciones_socias_f[f"{s['Id_Socia']} - {s['Nombre']}"] = s["Id_Socia"]

    socia_f = st.selectbox("Filtrar por socia:", list(opciones_socias_f.keys()))
    id_socia_f = opciones_socias_f[socia_f]

    opciones_tipo_f = {"Todos": None}
    for t in tipos:
        opciones_tipo_f[t["Tipo de multa"]] = t["Id_Tipo_multa"]

    tipo_f = st.selectbox("Filtrar por tipo:", opciones_tipo_f.keys())
    tipo_id_f = opciones_tipo_f[tipo_f]

    estado_f = st.selectbox("Estado:", ["Todos", "A pagar", "Pagada"])

    query = """
        SELECT M.Id_Multa, S.Id_Socia, S.Nombre, T.`Tipo de multa` AS Tipo,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1=1
    """

    params = []

    if fecha_sql:
        query += " AND M.Fecha_aplicacion=%s"
        params.append(fecha_sql)

    if id_socia_f:
        query += " AND M.Id_Socia=%s"
        params.append(id_socia_f)

    if tipo_id_f:
        query += " AND M.Id_Tipo_multa=%s"
        params.append(tipo_id_f)

    if estado_f != "Todos":
        query += " AND M.Estado=%s"
        params.append(estado_f)

    query += " ORDER BY M.Id_Multa DESC"

    cursor.execute(query, params)
    filtradas = cursor.fetchall()

    st.subheader("📋 Resultados filtrados")
    if filtradas:
        st.dataframe(pd.DataFrame(filtradas), hide_index=True)
    else:
        st.info("No hay registros.")

    st.markdown("---")

    # --------------------------
    # MULTAS PENDIENTES
    # --------------------------
    st.subheader("📌 Multas pendientes (A pagar)")

    cursor.execute("""
        SELECT M.Id_Multa, S.Id_Socia, S.Nombre, T.`Tipo de multa` AS Tipo,
               M.Monto, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE M.Estado='A pagar'
        ORDER BY M.Id_Multa DESC
    """)

    pendientes = cursor.fetchall()

    if not pendientes:
        st.info("No hay multas pendientes.")
    else:
        for m in pendientes:
            c1, c2, c3, c4, c5 = st.columns([1, 2, 2, 2, 3])
            c1.write(f"#{m['Id_Multa']}")
            c2.write(f"{m['Id_Socia']} - {m['Nombre']}")
            c3.write(m["Tipo"])
            c4.write(f"${m['Monto']}")

            if c5.button("Pagar", key=f"pay_{m['Id_Multa']}"):

                id_caja = obtener_o_crear_reunion(m["Fecha_aplicacion"])

                registrar_movimiento(
                    id_caja,
                    "Ingreso",
                    f"Pago de multa – {m['Nombre']}",
                    float(m["Monto"])
                )

                cursor.execute("UPDATE Multa SET Estado='Pagada' WHERE Id_Multa=%s", (m["Id_Multa"],))
                con.commit()
                st.success("✔ Multa pagada.")
                st.rerun()

    cursor.close()
    con.close()



# ============================================================
# ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    fecha_raw = st.date_input("Fecha de reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    cursor.execute("SELECT Id_Reunion FROM Reunion WHERE Fecha_reunion=%s", (fecha,))
    row = cursor.fetchone()

    if row:
        id_reunion = row["Id_Reunion"]
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
    for s in socias:
        estado = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["SI", "NO"],
            key=f"asis_{s['Id_Socia']}"
        )
        registro[s["Id_Socia"]] = estado

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
                    WHERE Id_Asistencia=%s
                """, (est, fecha, existe["Id_Asistencia"]))
            else:
                cursor.execute("""
                    INSERT INTO Asistencia(Id_Reunion, Id_Socia, Estado_asistencia, Fecha)
                    VALUES(%s,%s,%s,%s)
                """, (id_reunion, id_socia, est, fecha))

        con.commit()
        st.success("✔ Asistencia registrada.")

    cursor.execute("""
        SELECT S.Id_Socia, S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia=A.Id_Socia
        WHERE A.Id_Reunion=%s
    """, (id_reunion,))
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, hide_index=True)

    cursor.close()
    con.close()



# ============================================================
# REGISTRO DE SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    nombre = st.text_input("Nombre completo")
    dui_raw = st.text_input("DUI (9 dígitos, sin guion)", max_chars=9)

    dui_formateado = ""
    if dui_raw.isdigit() and len(dui_raw) == 9:
        dui_formateado = f"{dui_raw[:8]}-{dui_raw[8]}"
        st.success(f"Formato DUI: {dui_formateado}")
    else:
        st.info("Formato esperado: 00000000-0")

    telefono_raw = st.text_input("Teléfono (8 dígitos)", max_chars=8)

    if telefono_raw and not telefono_raw.isdigit():
        st.error("El teléfono solo debe contener números.")

    if st.button("Registrar socia"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        if not (dui_raw.isdigit() and len(dui_raw) == 9):
            st.error("DUI incorrecto.")
            return

        if not (telefono_raw.isdigit() and len(telefono_raw) == 8):
            st.error("Teléfono incorrecto.")
            return

        cursor.execute("""
            INSERT INTO Socia(Nombre, DUI, Telefono, Sexo)
            VALUES(%s,%s,%s,'F')
        """, (nombre, dui_formateado, telefono_raw))

        con.commit()
        st.success("✔ Socia registrada.")
        st.rerun()

    cursor.execute("SELECT Id_Socia, Nombre, DUI, Telefono FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, hide_index=True)

    cursor.close()
    con.close()
