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

    # BOTÓN DE CERRAR SESIÓN
    if st.sidebar.button("🔒 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

    # MOSTRAR SALDO REAL
    try:
        con = obtener_conexion()
        cur = con.cursor(dictionary=True)
        cur.execute("SELECT saldo_actual FROM caja_general WHERE id = 1")
        row = cur.fetchone()
        saldo = row["saldo_actual"] if row else 0
        st.info(f"💰 *Saldo actual de caja:* **${saldo:.2f}**")
    except:
        st.warning("⚠ No se pudo obtener el saldo actual de caja.")

    # MENÚ
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

    # RUTEO
    if menu == "Registro de asistencia":
        pagina_asistencia()

    elif menu == "Registrar nuevas socias":
        registrar_socia()  # ✅ CORREGIDO

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
# 🎯 REGISTRO DE ASISTENCIA
# ============================================================
def pagina_asistencia():

    st.header("📝 Registro de asistencia")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    fecha_raw = st.date_input("📅 Fecha de reunión:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    id_caja = obtener_o_crear_reunion(fecha)

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    st.subheader("Lista de asistencia")
    estados = {}

    for s in socias:
        eleccion = st.selectbox(
            f"{s['Id_Socia']} - {s['Nombre']}",
            ["Sí", "No"],
            key=f"asis_{s['Id_Socia']}"
        )
        estados[s["Id_Socia"]] = "Presente" if eleccion == "Sí" else "Ausente"

    if st.button("💾 Guardar asistencia"):
        for id_socia, estado in estados.items():

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

    cur.execute("""
        SELECT S.Nombre, A.Estado_asistencia
        FROM Asistencia A
        JOIN Socia S ON S.Id_Socia = A.Id_Socia
        WHERE A.Fecha = %s
    """, (fecha,))
    registros = cur.fetchall()

    if registros:
        st.subheader("📋 Asistencia registrada")
        st.dataframe(pd.DataFrame(registros), use_container_width=True)

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

    # INGRESOS EXTRAORDINARIOS
    st.subheader("💵 Registrar ingreso extraordinario (rifas, donaciones, etc.)")

    fecha_ing = st.date_input("📅 Fecha del ingreso:", date.today())
    fecha_ingreso = fecha_ing.strftime("%Y-%m-%d")

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    lista = cur.fetchall()
    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in lista}

    socia_sel = st.selectbox("Socia que aporta el ingreso:", list(dict_socias.keys()))
    id_socia_ing = dict_socias[socia_sel]

    concepto = st.selectbox("Concepto:", ["Rifa", "Donación", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.01, step=0.25)

    if st.button("➕ Registrar ingreso extraordinario"):

        id_caja = obtener_o_crear_reunion(fecha_ingreso)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Ingreso extraordinario — {concepto}",
            monto=monto
        )

        st.success("Ingreso extraordinario registrado y agregado a caja.")
        st.rerun()


# ============================================================
# REGISTRAR NUEVAS SOCIAS
# ============================================================
def registrar_socia():

    st.title("🤱 Registrar nuevas socias")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    nombre = st.text_input("Nombre completo de la socia:")

    dui = st.text_input(
        "Número de DUI (9 dígitos):",
        value="",
        max_chars=9,
        placeholder="XXXXXXXXX",
        key="dui_input",
        kwargs={
            "inputmode": "numeric",
            "pattern": "[0-9]{0,9}",
            "maxlength": "9"
        }
    )

    telefono = st.text_input(
        "Número de teléfono (8 dígitos):",
        value="",
        max_chars=8,
        placeholder="XXXXXXXX",
        key="telefono_input",
        kwargs={
            "inputmode": "numeric",
            "pattern": "[0-9]{0,8}",
            "maxlength": "8"
        }
    )

    distrito = st.text_input("Distrito asignado:")

    usuario = st.text_input("Usuario:")
    contrasena = st.text_input("Contraseña:", type="password")
    confirmar = st.text_input("Confirmar contraseña:", type="password")

    st.info("⚠️ Solo se permiten números y máximo 9 en DUI / 8 en Teléfono.")

    if st.button("Registrar socia"):

        if not nombre or not dui or not telefono or not distrito or not usuario or not contrasena:
            st.error("❌ Todos los campos son obligatorios.")
            return

        if contrasena != confirmar:
            st.error("❌ Las contraseñas no coinciden.")
            return

        if not dui.isnumeric() or len(dui) != 9:
            st.error("❌ El DUI debe tener exactamente 9 números.")
            return

        if not telefono.isnumeric() or len(telefono) != 8:
            st.error("❌ El teléfono debe tener exactamente 8 números.")
            return

        try:
            cursor.execute("""
                INSERT INTO socia (Nombre, DUI, Telefono, Distrito, Usuario, Contrasena)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, dui, telefono, distrito, usuario, contrasena))

            con.commit()
            st.success("✅ Socia registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error al registrar: {e}")

        finally:
            cursor.close()
            con.close()


# ============================================================
# MULTAS
# ============================================================
def pagina_multas():

    st.header("⚠️ Aplicar multas")

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()
    dict_socias = {s["Nombre"]: s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("Socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    cur.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM tipo_de_multa")
    tipos = cur.fetchall()
    dict_tipos = {t["Tipo_de_multa"]: t["Id_Tipo_multa"] for t in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", dict_tipos.keys())
    id_tipo = dict_tipos[tipo_sel]

    monto = st.number_input("Monto ($):", min_value=0.01, step=0.25)
    fecha_raw = st.date_input("Fecha:", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):

        cur.execute("""
            INSERT INTO Multa(Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
            VALUES(%s, %s, %s, %s, %s)
        """, (monto, fecha, estado, id_tipo, id_socia))

        con.commit()
        st.success("Multa registrada correctamente.")
        st.rerun()
