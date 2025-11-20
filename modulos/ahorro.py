import streamlit as st
import pandas as pd
from datetime import date
from modulos.config.conexion import obtener_conexion


# ---------------------------------------------------------
# 🟦 MÓDULO DE AHORROS
# ---------------------------------------------------------
def ahorro():

    st.header("💰 Registro y control de ahorros")

    con = obtener_conexion()
    if not con:
        st.error("❌ No se pudo conectar a la base de datos.")
        return

    cursor = con.cursor()

    # ============================================================
    # 1️⃣ SELECCIONAR SOCIA
    # ============================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre ASC")
    socias = cursor.fetchall()

    dict_socias = {nombre: id_socia for id_socia, nombre in socias}

    st.subheader("👩 Seleccione la socia")
    socia_sel = st.selectbox("Socia:", list(dict_socias.keys()))
    id_socia = dict_socias[socia_sel]

    st.markdown("---")

    # ============================================================
    # 2️⃣ REGISTRO DE APORTE DE AHORRO
    # ============================================================
    st.subheader("➕ Registrar aporte de ahorro")

    fecha_raw = st.date_input("📅 Fecha del aporte", value=date.today())
    fecha_aporte = fecha_raw.strftime("%Y-%m-%d")

    monto = st.number_input("💵 Monto del aporte ($)", min_value=0.00, step=0.50)
    tipo_aporte = st.selectbox("📌 Tipo de aporte", ["Ahorro ordinario", "Ahorro extraordinario"])
    comprobante = st.text_input("🧾 Comprobante digital (opcional)")

    # Obtener reunión del día
    cursor.execute("""
        SELECT Id_Reunion 
        FROM Reunion 
        WHERE Fecha_reunion = %s
    """, (fecha_aporte,))
    reunion = cursor.fetchone()

    if reunion:
        id_reunion = reunion[0]
    else:
        # Crear una reunión vacía si no existe (para registrar el ahorro)
        cursor.execute("""
            INSERT INTO Reunion (Fecha_reunion, observaciones, Acuerdos, Tema_central, Id_Grupo)
            VALUES (%s, '', '', '', 1)
        """, (fecha_aporte,))
        con.commit()
        id_reunion = cursor.lastrowid

    # ============================================================
    # BOTÓN – GUARDAR APORTE
    # ============================================================
    if st.button("💾 Registrar ahorro"):

        try:
            # 1️⃣ Obtener saldo acumulado actual del ahorro
            cursor.execute("""
                SELECT Saldo_acumulado
                FROM Ahorro
                WHERE Id_Socia = %s
                ORDER BY Id_Ahorro DESC
                LIMIT 1
            """, (id_socia,))
            row = cursor.fetchone()
            saldo_acumulado = row[0] if row else 0

            nuevo_saldo = saldo_acumulado + float(monto)

            # 2️⃣ Registrar aporte de ahorro
            cursor.execute("""
                INSERT INTO Ahorro
                (Fecha_del_aporte, Monto_del_aporte, Tipo_de_aporte, Comprobante_digital,
                 Saldo_acumulado, Id_Socia, Id_Reunion, Id_Grupo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """,
            (fecha_aporte, monto, tipo_aporte, comprobante, nuevo_saldo, id_socia, id_reunion))

            # 3️⃣ ACTUALIZAR CAJA → todo ahorro ingresa directo
            cursor.execute("""
                SELECT Saldo_actual
                FROM Caja
                ORDER BY Id_Caja DESC
                LIMIT 1
            """)
            row_saldo = cursor.fetchone()
            saldo_actual_caja = row_saldo[0] if row_saldo else 0

            nuevo_saldo_caja = saldo_actual_caja + float(monto)

            cursor.execute("""
                INSERT INTO Caja
                (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, 1, 2, %s)
            """,
            (f"Ahorro – {socia_sel}", monto, nuevo_saldo_caja, fecha_aporte))

            con.commit()
            st.success("✅ Aporte de ahorro registrado correctamente y sumado a caja.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar ahorro: {e}")

    st.markdown("---")

    # ============================================================
    # 3️⃣ HISTORIAL DE AHORRO POR SOCIA
    # ============================================================
    st.subheader(f"📋 Historial de ahorro – {socia_sel}")

    cursor.execute("""
        SELECT Fecha_del_aporte, Monto_del_aporte, Tipo_de_aporte, Saldo_acumulado
        FROM Ahorro
        WHERE Id_Socia = %s
        ORDER BY Id_Ahorro DESC
    """, (id_socia,))

    historial = cursor.fetchall()

    if historial:
        df = pd.DataFrame(historial, columns=["Fecha", "Monto", "Tipo", "Saldo acumulado"])
        st.dataframe(df)
        total = df["Monto"].sum()

        st.success(f"💰 Total aportado por {socia_sel}: ${total:.2f}")

    else:
        st.info("La socia no tiene aportes registrados.")
