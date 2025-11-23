import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # OBTENER SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today())

        socia_seleccionada = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[socia_seleccionada]

        monto = st.number_input("💵 Monto prestado ($):", min_value=1, step=1)
        tasa_interes = st.number_input("📈 Tasa de interés (%):", min_value=1, step=1)
        plazo = st.number_input("🗓 Plazo (meses):", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas:", min_value=1)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # ======================================================
        # VALIDAR AHORRO DE LA SOCIA
        # ======================================================
        cursor.execute("""
            SELECT `Saldo acumulado`
            FROM Ahorro
            WHERE Id_Socia=%s
            ORDER BY Id_Ahorro DESC
            LIMIT 1
        """, (id_socia,))

        registro_ahorro = cursor.fetchone()
        ahorro_total = float(registro_ahorro["Saldo acumulado"]) if registro_ahorro else 0.0

        if monto > ahorro_total:
            st.error(f"❌ La socia tiene solamente ${ahorro_total} ahorrados. No puede solicitar ${monto}.")
            return

        # ======================================================
        # VALIDAR CAJA
        # ======================================================
        cursor.execute("SELECT Id_Caja, Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        caja = cursor.fetchone()

        if not caja:
            st.error("❌ No existe caja activa.")
            return

        id_caja = caja["Id_Caja"]
        saldo_actual = caja["Saldo_actual"]

        if monto > saldo_actual:
            st.error(f"❌ Fondos insuficientes en caja. Saldo disponible: ${saldo_actual}")
            return

        saldo_pendiente = monto

        # ======================================================
        # REGISTRAR TODO
        # ======================================================
        try:
            # 1. PRÉSTAMO
            cursor.execute("""
                INSERT INTO Prestamo(
                    `Fecha del préstamo`, `Monto prestado`, `Tasa de interes`,
                    `Plazo`, `Cuotas`, `Saldo pendiente`, Estado_del_prestamo,
                    Id_Grupo, Id_Socia, Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha_prestamo,
                monto,
                tasa_interes,
                plazo,
                cuotas,
                saldo_pendiente,
                "activo",
                1,
                id_socia,
                id_caja
            ))

            # 2. EGRESO EN CAJA
            cursor.execute("""
                INSERT INTO Caja(Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, 1, 3, CURRENT_DATE())
            """,
            (
                f"Préstamo otorgado a: {socia_seleccionada}",
                -monto,
                saldo_actual - monto
            ))

            con.commit()

            st.success("✔ Préstamo autorizado correctamente.")

        except Exception as e:
            st.error(f"❌ Error al registrar el préstamo: {e}")
