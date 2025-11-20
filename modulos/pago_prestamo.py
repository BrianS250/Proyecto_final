import streamlit as st
import pandas as pd
from datetime import date
from modulos.config.conexion import obtener_conexion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor()

    # ============================================
    # 1️⃣ Seleccionar socia
    # ============================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Nombre ASC")
    socias = cursor.fetchall()
    socias_dict = {nombre: id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", socias_dict.keys())
    id_socia = socias_dict[socia_sel]

    # ============================================
    # 2️⃣ Buscar préstamos activos de la socia
    # ============================================
    cursor.execute("""
        SELECT Id_Préstamo, Fecha_del_préstamo, Monto_prestado, 
               Tasa_de_interes, Plazo, Cuotas, Saldo_pendiente
        FROM Prestamo
        WHERE Id_Socia = %s AND Estado_del_préstamo = 'Activo'
    """, (id_socia,))
    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    # Selección del préstamo
    prestamos_dict = {
        f"ID {p[0]} | Saldo pendiente: ${p[6]}": p[0]
        for p in prestamos
    }

    prestamo_sel = st.selectbox("📌 Seleccione el préstamo:", prestamos_dict.keys())
    id_prestamo = prestamos_dict[prestamo_sel]

    # Obtener datos del préstamo seleccionado
    datos = [p for p in prestamos if p[0] == id_prestamo][0]
    saldo_pendiente = datos[6]
    tasa_interes = datos[3]

    st.info(f"💰 **Saldo pendiente actual: ${saldo_pendiente}**")
    st.write(f"📌 Tasa de interés: **{tasa_interes}%** por cuota")

    # ============================================
    # 3️⃣ Monto del pago
    # ============================================
    fecha_pago = st.date_input("📅 Fecha del pago", value=date.today())
    monto_pago = st.number_input("💵 Monto abonado:", min_value=0.01, step=0.50)

    # Cálculo del interés de esta cuota
    interes_cuota = round(saldo_pendiente * (tasa_interes / 100), 2)
    capital_cuota = max(0, monto_pago - interes_cuota)

    st.write(f"🔹 Interés correspondiente: **${interes_cuota}**")
    st.write(f"🔹 Capital pagado: **${capital_cuota}**")

    # ============================================
    # 4️⃣ Registrar Pago
    # ============================================
    if st.button("💾 Registrar pago"):

        try:
            nuevo_saldo = saldo_pendiente - capital_cuota
            if nuevo_saldo < 0:
                nuevo_saldo = 0

            # Registrar en tabla pago del préstamo
            cursor.execute("""
                INSERT INTO `Pago del prestamo`
                (Fecha_de_pago, Monto_abonado, Interés_pagado, Capital_pagado, Saldo_restante, Id_Préstamo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (fecha_pago, monto_pago, interes_cuota, capital_cuota, nuevo_saldo, id_prestamo))

            # Actualizar saldo pendiente del préstamo
            estado_final = "Finalizado" if nuevo_saldo == 0 else "Activo"
            cursor.execute("""
                UPDATE Prestamo
                SET Saldo_pendiente = %s,
                    Estado_del_préstamo = %s
                WHERE Id_Préstamo = %s
            """, (nuevo_saldo, estado_final, id_prestamo))

            # Registrar movimiento en CAJA
            cursor.execute("""
                SELECT Saldo_actual
                FROM Caja
                ORDER BY Id_Caja DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            saldo_actual = row[0] if row else 0

            nuevo_saldo_caja = saldo_actual + monto_pago

            cursor.execute("""
                INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE())
            """,
            (
                f"Pago préstamo – {socia_sel}",
                monto_pago,
                nuevo_saldo_caja,
                1,
                2  # 2 = ingreso
            ))

            con.commit()
            st.success("Pago registrado correctamente y sumado a CAJA.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar el pago: {e}")

    # ============================================
    # 5️⃣ Mostrar historial
    # ============================================
    st.subheader("📜 Historial de pagos")

    cursor.execute("""
        SELECT Fecha_de_pago, Monto_abonado, Interés_pagado, Capital_pagado, Saldo_restante
        FROM `Pago del prestamo`
        WHERE Id_Préstamo = %s
        ORDER BY Fecha_de_pago ASC
    """, (id_prestamo,))
    pagos = cursor.fetchall()

    if pagos:
        df = pd.DataFrame(pagos, columns=[
            "Fecha", "Abonado", "Interés", "Capital", "Saldo restante"
        ])
        st.dataframe(df)
    else:
        st.info("Aún no hay pagos registrados.")
