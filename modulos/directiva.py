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
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_actual, obtener_reporte_reunion

# OTROS GASTOS
from modulos.gastos_grupo import gastos_grupo

# CIERRE DE CICLO
from modulos.cierre_ciclo import cierre_ciclo

# REGLAS INTERNAS
from modulos.reglas import gestionar_reglas
from modulos.reglas_utils import obtener_reglas



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

    # ============================================
    # FECHA GLOBAL (USADA SOLO PARA REPORTES)
    # ============================================
    if "fecha_global" not in st.session_state:
        st.session_state["fecha_global"] = date.today().strftime("%Y-%m-%d")

    fecha_sel = st.date_input(
        "📅 Fecha del reporte",
        value=pd.to_datetime(st.session_state["fecha_global"])
    ).strftime("%Y-%m-%d")

    st.session_state["fecha_global"] = fecha_sel

    # ============================================
    # SALDO GLOBAL (CAJA ÚNICA)
    # ============================================
    try:
        saldo_global = obtener_saldo_actual()
        st.success(f"💰 Saldo REAL en caja: **${saldo_global:.2f}**")
    except:
        st.error("⚠ No se pudo obtener el saldo actual.")

    # ============================================
    # REPORTE DEL DÍA SELECCIONADO
    # ============================================
    try:
        reporte = obtener_reporte_reunion(fecha_sel)

        ingresos = reporte["ingresos"]
        egresos = reporte["egresos"]
        balance = reporte["balance"]
        saldo_final = reporte["saldo_final"]

        st.subheader(f"📊 Reporte del día {fecha_sel}")

        st.info(
            f"""
            📥 **Ingresos del día:** ${ingresos:.2f}  
            📤 **Egresos del día:** ${egresos:.2f}  
            📘 **Balance del día:** ${balance:.2f}  
            🔚 **Saldo final registrado ese día:** ${saldo_final:.2f}
            """
        )

    except Exception as e:
        st.error(f"⚠ Error al generar reporte diario: {e}")

   

    # ============================================
    # MENÚ LATERAL
    # ============================================
    menu = st.sidebar.radio(
        "Menú rápido:",
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

    # ============================================================
    # 🔵 RESUMEN DEL CICLO (Conectado a Reglas Internas)
    # ============================================================
    from modulos.reglas_utils import obtener_reglas
    from modulos.conexion import obtener_conexion

    reglas = obtener_reglas()

    if reglas:
        fecha_inicio_ciclo = reglas.get("fecha_inicio_ciclo", None)

        if fecha_inicio_ciclo:

            st.markdown("---")
            st.subheader("📊 Resumen del ciclo (desde fecha definida en reglas)")

            con = obtener_conexion()
            cur = con.cursor(dictionary=True)

            cur.execute("""
                SELECT 
                    IFNULL(SUM(ingresos),0) AS total_ingresos,
                    IFNULL(SUM(egresos),0) AS total_egresos
                FROM caja_reunion
                WHERE fecha >= %s
            """, (fecha_inicio_ciclo,))

            tot = cur.fetchone()

            total_ingresos_ciclo = float(tot["total_ingresos"])
            total_egresos_ciclo = float(tot["total_egresos"])
            balance = total_ingresos_ciclo - total_egresos_ciclo

            st.write(f"📥 **Ingresos acumulados:** ${total_ingresos_ciclo:.2f}")
            st.write(f"📤 **Egresos acumulados:** ${total_egresos_ciclo:.2f}")
            st.write(f"💼 **Balance del ciclo:** ${balance:.2f}")

            cur.close()
            con.close()
        else:
            st.info("⚠ No está definida la fecha de inicio del ciclo en Reglas Internas.")
    else:
        st.info("⚠ Debes registrar reglas internas primero.")

    elif menu == "Reglas internas":
        gestionar_reglas()



# ============================================================
# MULTAS — TOTALMENTE CONECTADAS A REGLAS INTERNAS (FINAL)
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    # ---------------------------------------------
    # LEER REGLAS INTERNAS
    # ---------------------------------------------
    from modulos.reglas_utils import obtener_reglas
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ Debe registrar reglas internas primero.")
        return

    multa_inasistencia = float(reglas.get("multa_inasistencia", 0))
    multa_mora = float(reglas.get("multa_mora", 0))

    # ---------------------------------------------
    # CONEXIÓN A BD
    # ---------------------------------------------
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------
    # SOCIAS
    # ---------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    opciones_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ---------------------------------------------
    # TIPO DE MULTA
    # ---------------------------------------------
    tipo_sel = st.selectbox(
        "Tipo de multa:",
        ["Inasistencia", "Mora préstamo", "Otra"]
    )

    # Monto automático desde reglas
    if tipo_sel == "Inasistencia":
        monto_default = multa_inasistencia
        editable = False
    elif tipo_sel == "Mora préstamo":
        monto_default = multa_mora
        editable = False
    else:
        monto_default = 0.25
        editable = True

    # ---------------------------------------------
    # FORMULARIO DE NUEVA MULTA
    # ---------------------------------------------
    st.subheader("➕ Registrar nueva multa")

    socia_sel = st.selectbox("👩 Socia:", opciones_socias.keys())
    id_socia = opciones_socias[socia_sel]

    fecha = st.date_input("📅 Fecha", date.today()).strftime("%Y-%m-%d")

    monto = st.number_input(
        "Monto ($)",
        min_value=0.25,
        step=0.25,
        value=monto_default,
        disabled=not editable
    )

    estado_sel = st.selectbox("Estado:", ["A pagar", "Pagada"])

    # ---------------------------------------------
    # VALIDACIÓN PERMISO
    # NO aplicar multa si tiene permiso
    # ---------------------------------------------
    cursor.execute("""
        SELECT Estado_asistencia
        FROM Asistencia
        WHERE Id_Socia=%s AND Fecha=%s
        LIMIT 1
    """, (id_socia, fecha))
    row_asistencia = cursor.fetchone()

    if row_asistencia and row_asistencia["Estado_asistencia"] == "Permiso":
        st.warning("🔒 La socia tenía PERMISO. No se puede aplicar multa.")
        return

    # ---------------------------------------------
    # GUARDAR MULTA
    # ---------------------------------------------
    if st.button("💾 Registrar multa"):

        cursor.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES (%s, %s, %s, NULL, %s)
        """, (monto, fecha, estado_sel, id_socia))

        con.commit()
        st.success("✔ Multa registrada correctamente.")
        st.rerun()

    st.markdown("---")

    # ---------------------------------------------
    # FILTROS
    # ---------------------------------------------
    st.subheader("🔎 Filtrar multas")

    fecha_filtro = st.date_input("Fecha (opcional):", value=None)
    fecha_sql = fecha_filtro.strftime("%Y-%m-%d") if fecha_filtro else None

    socia_f = st.selectbox("Filtrar por socia:", ["Todas"] + list(opciones_socias.keys()))
    id_socia_f = None if socia_f == "Todas" else opciones_socias[socia_f]

    estado_f = st.selectbox("Estado:", ["Todos", "A pagar", "Pagada"])

    # QUERY
    query = """
        SELECT M.Id_Multa, S.Id_Socia, S.Nombre,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        WHERE 1=1
    """
    params = []

    if fecha_sql:
        query += " AND Fecha_aplicacion=%s"
        params.append(fecha_sql)

    if id_socia_f:
        query += " AND M.Id_Socia=%s"
        params.append(id_socia_f)

    if estado_f != "Todos":
        query += " AND M.Estado=%s"
        params.append(estado_f)

    query += " ORDER BY M.Id_Multa DESC"

    cursor.execute(query, params)
    filtradas = cursor.fetchall()

    st.dataframe(pd.DataFrame(filtradas), hide_index=True)

    st.markdown("---")

    # ---------------------------------------------
    # MULTAS PENDIENTES
    # ---------------------------------------------
    st.subheader("📌 Multas pendientes (A pagar)")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, M.Monto, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia = M.Id_Socia
        WHERE Estado='A pagar'
        ORDER BY Id_Multa DESC
    """)

    pendientes = cursor.fetchall()

    if not pendientes:
        st.info("No hay multas pendientes.")
    else:
        for m in pendientes:
            c1, c2, c3, c4 = st.columns([1, 2, 2, 2])
            c1.write(f"#{m['Id_Multa']}")
            c2.write(m["Nombre"])
            c3.write(f"${m['Monto']}")

            if c4.button("Pagar", key=f"pay_{m['Id_Multa']}"):

                id_caja = obtener_o_crear_reunion(m["Fecha_aplicacion"])

                registrar_movimiento(
                    id_caja=id_caja,
                    tipo="Ingreso",
                    categoria=f"Pago multa {m['Nombre']}",
                    monto=float(m["Monto"])
                )

                cursor.execute("""
                    UPDATE Multa
                    SET Estado='Pagada'
                    WHERE Id_Multa=%s
                """, (m["Id_Multa"],))

                con.commit()
                st.success("✔ Pago registrado.")
                st.rerun()

    cursor.close()
    con.close()


# ============================================================
# ASISTENCIA — CONECTADA A REGLAS INTERNAS
# ============================================================
def pagina_asistencia():

    from modulos.reglas_utils import obtener_reglas

    st.header("📝 Registro de asistencia")

    # ---------------------------------------------
    # LEER REGLAS INTERNAS
    # ---------------------------------------------
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No hay reglas internas registradas.")
        return

    multa_inasistencia = float(reglas["multa_inasistencia"])

    # ---------------------------------------------
    # CONEXIÓN
    # ---------------------------------------------
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------
    # FECHA DE LA REUNIÓN
    # ---------------------------------------------
    fecha_raw = st.date_input("📅 Fecha de reunión", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # ---------------------------------------------
    # OBTENER O CREAR REUNIÓN
    # ---------------------------------------------
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

    # ---------------------------------------------
    # SOCIAS
    # ---------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    st.subheader("Lista de asistencia")

    registro = {}
    for s in socias:
        estado = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["Presente", "Ausente", "Permiso"],
            key=f"asis_{s['Id_Socia']}"
        )
        registro[s["Id_Socia"]] = estado

    # ---------------------------------------------
    # GUARDAR ASISTENCIA
    # ---------------------------------------------
    if st.button("💾 Guardar asistencia"):

        for id_socia, estado in registro.items():

            # -----------------------------------
            # Determinar estado a guardar
            # -----------------------------------
            if estado == "Presente":
                est = "Presente"

            elif estado == "Permiso":
                est = "Permiso"  # NO MULTA

            else:  # Ausente
                est = "Ausente"

                # MULTA automática por inasistencia
                cursor.execute("""
                    INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                    VALUES (%s, %s, 'A pagar', 1, %s)
                """, (multa_inasistencia, fecha, id_socia))

            # -----------------------------------
            # Insert/update en asistencia
            # -----------------------------------
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
        st.success("✔ Asistencia registrada correctamente (reglas aplicadas).")
        st.rerun()

    # ---------------------------------------------
    # MOSTRAR ASISTENCIA DEL DÍA
    # ---------------------------------------------
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
