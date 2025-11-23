import streamlit as st
import pandas as pd
from datetime import date

from modulos.conexion import obtener_conexion

# MÓDULOS EXTERNOS
from modulos.autorizar_prestamo import autorizar_prestamo
from modulos.pago_prestamo import pago_prestamo
from modulos.ahorro import ahorro
from modulos.gastos_grupo import gastos_grupo
from modulos.reporte_caja import reporte_caja
from modulos.reglas import gestionar_reglas
from modulos.cierre_ciclo import cierre_ciclo

# CAJA ÚNICA POR REUNIÓN
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# PANEL PRINCIPAL — DIRECTIVA
# ============================================================
def interfaz_directiva():

    rol = st.session_state.get("rol", "")

    if rol != "Director":
        st.title("Acceso denegado")
        st.warning("Solo el Director puede acceder a esta sección.")
        return

    st.title("👩‍💼 Panel de Directiva — Solidaridad CVX")

    # -------------------------------------------
    # BOTÓN DE CERRAR SESIÓN
    # -------------------------------------------
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # -------------------------------------------
    # MOSTRAR SALDO DE CAJA (último saldo_final)
    # -------------------------------------------
    try:
        con = obtener_conexion()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
        row = cur.fetchone()
        saldo = row["saldo_final"] if row else 0
        st.info(f"💰 *Saldo actual de caja:* **${saldo:.2f}**")
    except:
        st.warning("⚠ No se pudo obtener el saldo actual de caja.")

    # -------------------------------------------
    # MENÚ LATERAL — ORDEN FINAL SOLICITADO
    # -------------------------------------------
    menu = st.sidebar.radio(
        "📌 Selección rápida:",
        [
            "Registro de asistencia",
            "Registrar nuevas socias",
            "Reglas internas",
            "Registrar ahorro",
            "Aplicar multas",
            "Autorizar préstamo",
            "Registrar pago de préstamo",
            "Gastos del grupo",
            "Reporte de caja",
            "Cierre de ciclo",
        ]
    )

    # -------------------------------------------
    # RUTEO DE TODAS LAS FUNCIONES
    # -------------------------------------------
    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Registrar nuevas socias":
        pagina_registro_socias()

    elif menu == "Reglas internas":
        gestionar_reglas()

    elif menu == "Registrar ahorro":
        ahorro()

    elif menu == "Aplicar multas":
        pagina_multas()

    elif menu == "Autorizar préstamo":
        autorizar_prestamo()

    elif menu == "Registrar pago de préstamo":
        pago_prestamo()

    elif menu == "Gastos del grupo":
        gastos_grupo()

    elif menu == "Reporte de caja":
        reporte_caja()

    elif menu == "Cierre de ciclo":
        cierre_ciclo()


# ============================================================
# 🎯 REGISTRO DE ASISTENCIA — ***MEJORADO SIN ROMPER NADA***
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # -------------------------------------------
    # Selección de fecha
    # -------------------------------------------
    fecha_raw = st.date_input("📅 Fecha de reunión:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # -------------------------------------------
    # Crear o recuperar reunión (caja del día)
    # -------------------------------------------
    id_caja = obtener_o_crear_reunion(fecha)

    # -------------------------------------------
    # Obtener lista de socias
    # -------------------------------------------
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    st.subheader("Lista de asistencia")
    estados = {}

    # -------------------------------------------
    # Formulario por socia
    # -------------------------------------------
    for s in socias:
        estados[s["Id_Socia"]] = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["Presente", "Ausente"],
            key=f"asis_{s['Id_Socia']}"
        )

    # -------------------------------------------
    # Guardar asistencia
    # -------------------------------------------
    if st.button("💾 Guardar asistencia"):
        for id_socia, estado in estados.items():

            # ¿Ya existe registro?
            cur.execute("""
                SELECT Id_Asistencia
                FROM Asistencia
                WHERE Id_Socia = %s AND Fecha = %s
            """, (id_socia, fecha))

            existe = cur.fetchone()

            if existe:
                cur.execute("""
                    UPDATE Asistencia
                    SET Estado_asistencia=%s
                    WHERE Id_Asistencia=%s
                """, (estado, existe["Id_Asistencia"]))

            else:
                cur.execute("""
                    INSERT INTO Asistencia(Id_Socia,Fecha,Estado_asistencia,Id_Reunion)
                    VALUES(%s,%s,%s,%s)
                """, (id_socia, fecha, estado, id_caja))

        con.commit()
        st.success("Asistencia guardada correctamente.")
        st.rerun()

    # -------------------------------------------
    # Mostrar TOT ALES DE ASISTENCIA
    # -------------------------------------------
    cur.execute("""
        SELECT Estado_asistencia
        FROM Asistencia
        WHERE Fecha = %s
    """, (fecha,))
    registros_tot = cur.fetchall()

    if registros_tot:
        total_socias = len(registros_tot)
        presentes = sum(1 for r in registros_tot if r["Estado_asistencia"] == "Presente")
        ausentes = total_socias - presentes

        st.subheader("📊 Resumen de asistencia")
        st.info(
            f"👩‍🦰 Total socias: **{total_socias}**\n"
            f"🟢 Presentes: **{presentes}**\n"
            f"🔴 Ausentes: **{ausentes}**"
        )

    st.markdown("---")

    # ----------------------------------------------------------
    # ⭐ INGRESOS EXTRAORDINARIOS
    # ----------------------------------------------------------
    st.subheader("💵 Registrar ingreso extraordinario (rifas, donaciones, etc.)")

    concepto = st.text_input("Concepto del ingreso:")
    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):

        if concepto.strip() == "":
            st.warning("Debe ingresar un concepto.")
        else:
            registrar_movimiento(
                id_caja=id_caja,
                tipo="Ingreso",
                categoria=f"Ingreso extraordinario — {concepto}",
                monto=monto
            )

            st.success("Ingreso extraordinario registrado y agregado a caja.")
            st.rerun()

    # -------------------------------------------
    # Mostrar registro guardado
    # -------------------------------------------
    cur.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Fecha = %s
    """, (fecha,))
    registros = cur.fetchall()

    if registros:
        df = pd.DataFrame(registros)
        st.dataframe(df, use_container_width=True)


# ============================================================
# 👩‍🦰 REGISTRAR NUEVAS SOCIAS
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registrar nuevas socias")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    nombre = st.text_input("Nombre completo de la socia:")

    if st.button("Registrar socia"):
        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        cur.execute("""
            INSERT INTO Socia(Nombre, Sexo)
            VALUES(%s, 'F')
        """, (nombre,))
        con.commit()

        st.success(f"Socia '{nombre}' registrada correctamente.")
        st.rerun()

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    data = cur.fetchall()

    if data:
        df = pd.DataFrame(data)
        st.subheader("📋 Lista de socias")
        st.dataframe(df, use_container_width=True)


# ============================================================
# ⚠️ APLICACIÓN DE MULTAS
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicar multas")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ----------------------------------------------------------
    # SOCIAS
    # ----------------------------------------------------------
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()
    dict_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ----------------------------------------------------------
    # TIPOS DE MULTA
    # ----------------------------------------------------------
    cur.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM tipo_de_multa")
    tipos = cur.fetchall()
    dict_tipos = {t["Tipo_de_multa"]: t["Id_Tipo_multa"] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", dict_tipos.keys())
    id_tipo = dict_tipos[tipo_sel]

    # ----------------------------------------------------------
    # DATOS DE LA MULTA
    # ----------------------------------------------------------
    monto = st.number_input("Monto ($):", min_value=0.01, step=0.25)
    fecha_raw = st.date_input("Fecha:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    # ----------------------------------------------------------
    # GUARDAR MULTA
    # ----------------------------------------------------------
    if st.button("💾 Registrar multa"):

        cur.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES(%s, %s, %s, %s, %s)
        """, (monto, fecha, estado, id_tipo, id_socia))

        con.commit()
        st.success("Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")
    st.subheader("📋 Multas registradas")

    # ----------------------------------------------------------
    # FILTROS
    # ----------------------------------------------------------
    filtro_socia = st.selectbox("Filtrar por socia:", ["Todas"] + list(dict_socias.keys()))
    filtro_estado = st.selectbox("Estado:", ["Todos", "A pagar", "Pagada"])

    query = """
        SELECT M.Id_Multa, S.Nombre AS Socia, T.Tipo_de_multa,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        JOIN tipo_de_multa T ON T.Id_Tipo_multa = M.Id_Tipo_multa
        WHERE 1 = 1
    """
    params = []

    if filtro_socia != "Todas":
        query += " AND S.Nombre = %s"
        params.append(filtro_socia)

    if filtro_estado != "Todos":
        query += " AND M.Estado = %s"
        params.append(filtro_estado)

    query += " ORDER BY M.Id_Multa DESC"

    cur.execute(query, params)
    multas = cur.fetchall()

    # ----------------------------------------------------------
    # MOSTRAR MULTAS
    # ----------------------------------------------------------
    for m in multas:

        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 3, 3, 2, 2, 2, 2])

        col1.write(m["Id_Multa"])
        col2.write(m["Socia"])
        col3.write(m["Tipo_de_multa"])
        col4.write(f"${m['Monto']:.2f}")

        nuevo_estado = col5.selectbox(
            " ",
            ["A pagar", "Pagada"],
            index=0 if m["Estado"] == "A pagar" else 1,
            key=f"multa_{m['Id_Multa']}"
        )

        col6.write(str(m["Fecha_aplicacion"]))

        if col7.button("Actualizar", key=f"u_{m['Id_Multa']}"):

            estado_anterior = m["Estado"]

            # SI pasa de A pagar → Pagada → suma a caja
            if estado_anterior == "A pagar" and nuevo_estado == "Pagada":

                cur.execute("SELECT id_caja FROM caja_reunion WHERE fecha = %s", (m["Fecha_aplicacion"],))
                reunion = cur.fetchone()

                if reunion:
                    id_caja = reunion["id_caja"]

                    registrar_movimiento(
                        id_caja=id_caja,
                        tipo="Ingreso",
                        categoria=f"Pago multa ({m['Socia']})",
                        monto=float(m["Monto"])
                    )

            cur.execute("""
                UPDATE Multa
                SET Estado = %s
                WHERE Id_Multa = %s
            """, (nuevo_estado, m["Id_Multa"]))

            con.commit()
            st.success("Multa actualizada correctamente.")
            st.rerun()


# ============================================================
# FIN DEL MÓDULO DIRECTIVA
# ============================================================
