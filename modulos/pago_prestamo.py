import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion

def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor()

    # 1️⃣ Seleccionar socia
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre ASC")
    socias = cursor.fetchall()
    lista_socias = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", lista_socias.keys())
    id_socia = lista_socias[socia_sel]

    # 2️⃣ Obtener préstamos activos
    cursor.execute("""
        SELECT 
            `Id_Préstamo`,
            `Fecha del préstamo`,
            `Monto prestado`,
            `Tasa de interes`,
            `Plazo`,
            `Cuotas`,
            `Saldo pendiente`,
            `Estado del préstamo`
        FROM Prestamo
        WHERE Id_Socia = %s AND `Estado del préstamo` = 'Activo'
    """, (id_socia,))

    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    df = pd.DataFrame(prestamos, columns=[
        "ID", "Fecha", "Monto", "Interés", "Plazo", "Cuotas", "Saldo pendiente", "Estado"
    ])
    st.dataframe(df)

    # 3️⃣ Seleccionar préstamo
    id_prestamo = st.selectbox("Seleccione el préstamo a pagar:", df["ID"].tolist())

    # 4️⃣ Monto pagado
    monto_pago = st.number_input("Monto abonado ($):", min_value=0.00, step=0.50)
    fecha_pago = st.date_input("Fecha del pago", value=date.today())

    if st.button("Registrar pago"):

        # Obtener saldo actual del préstamo
        cursor.execute("SELECT `Saldo pendiente` FROM Prestamo WHERE Id_Préstamo = %s", (id_prestamo,))
        saldo_pend = cursor.fetchone()[0]

        nuevo_saldo = saldo_pend - float(monto_pago)
        if nuevo_saldo < 0:
            nuevo_saldo = 0

        # Guardar pago
        cursor.execute("""
            INSERT INTO `Pago del préstamo`
            (Fecha_de_pago, Monto_abonado, Interés_pagado, Capital_pagado, Saldo_restante, Id_Préstamo, Id_Caja)
            VALUES (%s, %s, 0, %s, %s, %s, NULL)
        """, (fecha_pago, monto_pago, monto_pago, nuevo_saldo, id_prestamo))

        # Actualizar saldo pendiente
        cursor.execute("""
            UPDATE Prestamo
            SET `Saldo pendiente` = %s,
                `Estado del préstamo` = %s
            WHERE Id_Préstamo = %s
        """, (
            nuevo_saldo,
            "Finalizado" if nuevo_saldo == 0 else "Activo",
            id_prestamo,
        ))

        # Actualizar CAJA
        cursor.execute("""
            SELECT Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1
        """)
        row = cursor.fetchone()
        saldo_actual = row[0] if row else 0

        nuevo = saldo_actual + float(monto_pago)

        cursor.execute("""
            INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
            VALUES (%s, %s, %s, 1, 2, CURRENT_DATE())
        """, (f"Pago préstamo – {socia_sel}", monto_pago, nuevo))

        con.commit()
        st.success("Pago registrado correctamente.")
        st.rerun()
