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
# PANEL PRINCIPAL
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
            "Reglas internas"     # ← AGREGADO
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

        # =====================================================
        # 🔵 CONTADOR DE SOCIAS — YA INTEGRADO
        # =====================================================
        total_socias = len(datos)
        presentes = sum(1 for _, est in datos if est == "Presente")
        ausentes = total_socias - presentes

        st.markdown("### 📊 Resumen de asistencia")

        c1, c2, c3 = st.columns(3)
        c1.metric("Total de socias", total_socias)
        c2.metric("Presentes", presentes)
        c3.metric("Ausentes", ausentes)

    st.markdown("---")

    # ============================================================
    # INGRESOS EXTRAORDINARIOS
    # ============================================================
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
# MULTAS
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
    st.subheader("📋 Multas registradas")

    cursor.execute("""
        SELECT M.Id_Multa, S.Nombre, T.`Tipo de multa`,
               M.Monto, M.Estado, M.Fecha_aplicacion
        FROM Multa M
        JOIN Socia S ON S.Id_Socia=M.Id_Socia
        JOIN `Tipo de multa` T ON T.Id_Tipo_multa=M.Id_Tipo_multa
        ORDER BY M.Id_Multa DESC
    """)
    multas = cursor.fetchall()

    for mid, nombre, tipo, monto, estado_actual, fecha_m in multas:

        c1, c2, c3, c4, c5, c6 = st.columns([1,3,3,2,2,2])

        c1.write(mid)
        c2.write(nombre)
        c3.write(tipo)
        c4.write(f"${monto}")

        nuevo_estado = c5.selectbox(
            " ",
            ["A pagar", "Pagada"],
            index=0 if estado_actual == "A pagar" else 1,
            key=f"upd{mid}"
        )

        if c6.button("Actualizar", key=f"btn{mid}"):

            if estado_actual == "A pagar" and nuevo_estado == "Pagada":

                id_caja = obtener_o_crear_reunion(fecha_m)
                registrar_movimiento(
                    id_caja,
                    "Ingreso",
                    f"Pago de multa – {nombre}",
                    monto
                )

            cursor.execute("""
                UPDATE Multa SET Estado=%s WHERE Id_Multa=%s
            """, (nuevo_estado, mid))

            con.commit()
            st.success(f"Multa {mid} actualizada.")
            st.rerun()



# ============================================================
# REGISTRO DE SOCIAS  (DUI con guion automático)
# ============================================================
def pagina_registro_socias():

    st.header("👩‍🦰 Registro de nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor()

    # --------------------------
    # NOMBRE
    # --------------------------
    nombre = st.text_input("Nombre completo")

    # --------------------------
    # DUI — guion automático después de 8 dígitos
    # --------------------------
    dui_raw = st.text_input("DUI (00000000-0)", max_chars=10)

    # Quitar cualquier cosa que no sea número
    digitos = "".join([c for c in dui_raw if c.isdigit()])

    # Limitar máximo a 9 dígitos
    digitos = digitos[:9]

    # Construir DUI formateado automáticamente
    if len(digitos) > 8:
        dui_formateado = digitos[:8] + "-" + digitos[8]
    else:
        dui_formateado = digitos

    # Mostrar el DUI formateado debajo del input (sin modificar el input directamente)
    st.caption(f"🔎 DUI detectado: `{dui_formateado}`")

    # --------------------------
    # TELÉFONO — solo números
    # --------------------------
    tel_raw = st.text_input("Número de teléfono (8 dígitos)", max_chars=8)
    telefono = "".join([c for c in tel_raw if c.isdigit()])
    telefono = telefono[:8]

    st.caption(f"📞 Teléfono detectado: `{telefono}`")

    # --------------------------
    # GUARDAR SOCIA
    # --------------------------
    if st.button("Registrar socia"):

        if nombre.strip() == "":
            st.warning("Debe ingresar un nombre.")
            return

        if len(digitos) != 9:
            st.warning("El DUI debe contener 9 dígitos (00000000-0).")
            return

        if len(telefono) != 8:
            st.warning("El teléfono debe tener exactamente 8 dígitos.")
            return

        cursor.execute("""
            INSERT INTO Socia(Nombre, DUI, Telefono, Sexo)
            VALUES(%s, %s, %s, 'F')
        """, (nombre, dui_formateado, telefono))

        con.commit()

        st.success("Socia registrada correctamente.")
        st.rerun()

    # --------------------------
    # MOSTRAR TABLA DE SOCIAS
    # --------------------------
    cursor.execute("SELECT Id_Socia, Nombre, DUI, Telefono FROM Socia ORDER BY Id_Socia ASC")
    datos = cursor.fetchall()

    if datos:
        df = pd.DataFrame(datos, columns=["ID","Nombre","DUI","Telefono"])
        st.dataframe(df)
