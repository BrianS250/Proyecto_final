import streamlit as st
import pandas as pd
from datetime import date
from modulos.config.conexion import obtener_conexion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS CON ID (CORREGIDO)
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ BUSCAR PRÉSTAMOS ACTIVOS DE ESA SOCIA (CORREGIDO)
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT 
            Id_Préstamo,
            Fecha_del_préstamo,
            Monto_prestado,
            Saldo_pendiente,
            Cuotas,
            Tasa_de_interes,
            Plazo
        FROM Prestamo
        WHERE Id_Socia = %s AND Estado_del_préstamo = 'Activo'
    """, (id_socia,))
    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    # ---------------------------------------------------------
    # 3️⃣ SELECT DEL PRÉSTAMO
    # ---------------------------------------------------------
    opciones = {
        f"ID {p[0]} | Prestado: ${p[2]} | Saldo: ${p[3]}": p[0] for p in prestamos
    }

    prestamo_sel = st.selectbox("📌 Seleccione el préstamo:", list(opciones.keys()))
    id_prestamo = opciones[prestamo_sel]

    # ---------------------------------------------------------
    # 4️⃣ MOSTRAR DATOS DEL PRÉSTAMO SELECCIONADO
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT 
            Fecha_del_préstamo, 
            Monto_prestado, 
            Saldo_pendiente, 
            Tasa_de_interes,
            Plazo,
            Cuotas
        FROM Prestamo
        WHERE Id_Préstamo = %s
    """, (id_prestamo,))

    datos = cursor.fetchone()
    fecha_prestamo, monto_prestado, saldo_pendiente, tasa, plazo, cuotas = datos

    st.subheader("📄 Información del préstamo")
    st.write(f"**Fecha del préstamo:** {fecha_prestamo}")
    st.write(f"**Monto prestado:** ${monto_prestado}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")
    st.write(f"**Tasa de interés:** {tasa}%")
    st.write(f"**Plazo:** {plazo} meses")
    st.write(f"**Cuotas:** {cuotas}")

    # ---------------------------------------------------------
    # 5️⃣ FORMULARIO DE PAGO
    # ---------------------------------------------------------
    st.markdown("---")
    st.header("🧾 Registrar pago")

    fecha_pago_raw = st.date_input("📅 Fecha del pago:", value=date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.01, step=0.50)

    if st.button("💾 Registrar pago"):

        try:
            # ---------------------------------------------------------
            # 6️⃣ INSERTAR PAGO EN TABLA Pago_del_prestamo
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO Pago_del_prestamo
                (Fecha_de_pago, Monto_abonado, Interés_pagado, Capital_pagado, Saldo_restante, Id_Préstamo)
                VALUES (%s, %s, 0, 0, 0, %s)
            """, (fecha_pago, monto_abonado, id_prestamo))

            # Calcular nuevo saldo
            nuevo_saldo = saldo_pendiente - float(monto_abonado)
            if nuevo_saldo < 0:
                nuevo_saldo = 0

            # ---------------------------------------------------------
            # 7️⃣ ACTUALIZAR PRÉSTAMO
            # ---------------------------------------------------------
            cursor.execute("""
                UPDATE Prestamo
                SET Saldo_pendiente = %s,
                    Estado_del_préstamo = CASE WHEN %s = 0 THEN 'Cancelado' ELSE 'Activo' END
                WHERE Id_Préstamo = %s
            """, (nuevo_saldo, nuevo_saldo, id_prestamo))

            # ---------------------------------------------------------
            # 8️⃣ SUMAR A CAJA (INGRESO)
            # ---------------------------------------------------------
            cursor.execute("""
                SELECT Saldo_actual
                FROM Caja
                ORDER BY Id_Caja DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            saldo_actual = row[0] if row else 0

            nuevo_saldo_caja = saldo_actual + float(monto_abonado)

            cursor.execute("""
                INSERT INTO Caja 
                (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha, Id_Préstamo)
                VALUES (%s, %s, %s, %s, %s, CURRENT_DATE(), %s)
            """, (
                f"Pago de préstamo – Socia {id_socia}",
                monto_abonado,
                nuevo_saldo_caja,
                1,
                2,    # INGRESO
                id_prestamo
            ))

            con.commit()
            st.success("Pago registrado correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")
