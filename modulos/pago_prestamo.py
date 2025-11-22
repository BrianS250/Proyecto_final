import streamlit as st
from datetime import date
from decimal import Decimal
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
#        REGISTRO DE PAGOS DE PRÉSTAMOS — SISTEMA CVX
# ============================================================
def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s['Id_Socia'] for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ PRÉSTAMOS ACTIVOS
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))

    prestamo = cursor.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    monto = Decimal(prestamo["Monto prestado"])
    saldo_pendiente = Decimal(prestamo["Saldo pendiente"])
    tasa = Decimal(prestamo["Tasa de interes"])
    cuotas = prestamo["Cuotas"]

    # Interés total ya calculado al autorizar
    interes_total = Decimal(prestamo["Interes_total"])
    interes_por_cuota = interes_total / Decimal(cuotas)
    total_a_pagar = monto + interes_total
    cuota_fija = total_a_pagar / Decimal(cuotas)
    capital_por_cuota = cuota_fija - interes_por_cuota

    # ---------------------------------------------------------
    # 3️⃣ MOSTRAR INFORMACIÓN
    # ---------------------------------------------------------
    st.subheader("📄 Información del préstamo")
    st.write(f"**Monto prestado:** ${monto}")
    st.write(f"**Interés total:** ${interes_total:.2f}")
    st.write(f"**Total a pagar:** ${total_a_pagar:.2f}")
    st.write(f"**Cuotas:** {cuotas}")
    st.write(f"**Cuota fija:** ${cuota_fija:.2f}")
    st.write(f"**Capital por cuota:** ${capital_por_cuota:.2f}")
    st.write(f"**Interés por cuota:** ${interes_por_cuota:.2f}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente:.2f}")

    # ---------------------------------------------------------
    # 4️⃣ FORMULARIO DE PAGO
    # ---------------------------------------------------------
    st.markdown("---")
    fecha_pago_raw = st.date_input("📅 Fecha de pago", value=date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    if st.button("💾 Registrar pago"):

        try:
            # ---------------------------------------------------------
            # 5️⃣ CONTROLAR QUE NO SE PAGUE MÁS DE LO QUE DEBE
            # ---------------------------------------------------------
            abono = cuota_fija
            if abono > saldo_pendiente:
                abono = saldo_pendiente

            interes_pagado = interes_por_cuota if saldo_pendiente >= cuota_fija else 0
            capital_pagado = abono - interes_pagado

            nuevo_saldo = saldo_pendiente - abono
            if nuevo_saldo < 0:
                nuevo_saldo = 0

            # ---------------------------------------------------------
            # 6️⃣ REGISTRO EN CAJA (sistema nuevo caja_reunion)
            # ---------------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_pago)

            registrar_movimiento(
                id_caja=id_caja,
                tipo="Ingreso",
                categoria=f"Pago préstamo — {socia_sel}",
                monto=abono
            )

            # ---------------------------------------------------------
            # 7️⃣ REGISTRAR EL PAGO EN TABLA CORRECTA
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO Pago_del_prestamo (
                    `Fecha de pago`,
                    `Monto abonado`,
                    `Interés pagado`,
                    `Capital pagado`,
                    `Saldo restante`,
                    Id_Prestamo,
                    Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                fecha_pago,
                float(abono),
                float(interes_pagado),
                float(capital_pagado),
                float(nuevo_saldo),
                id_prestamo,
                id_caja
            ))

            # ---------------------------------------------------------
            # 8️⃣ ACTUALIZAR PRÉSTAMO
            # ---------------------------------------------------------
            nuevo_estado = "pagado" if nuevo_saldo == 0 else "activo"

            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=%s,
                    Estado_del_prestamo=%s
                WHERE Id_Préstamo=%s
            """, (float(nuevo_saldo), nuevo_estado, id_prestamo))

            con.commit()
            st.success("✔ Pago registrado correctamente.")

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")

    # ---------------------------------------------------------
    # 9️⃣ HISTORIAL DE PAGOS
    # ---------------------------------------------------------
    st.subheader("📜 Historial de pagos")

    cursor.execute("""
        SELECT *
        FROM Pago_del_prestamo
        WHERE Id_Prestamo=%s
        ORDER BY Id_Pago ASC
    """, (id_prestamo,))

    pagos = cursor.fetchall()

    if pagos:
        import pandas as pd
        st.dataframe(pd.DataFrame(pagos), hide_index=True)
    else:
        st.info("No hay pagos registrados aún.")

    cursor.close()
    con.close()
