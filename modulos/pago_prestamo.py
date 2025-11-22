import streamlit as st
import pandas as pd
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
#    REGISTRAR PAGO DE PRÉSTAMO — SISTEMA CVX
# ============================================================
def pago_prestamo():

    st.title("💵 Registrar pago de préstamo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("No hay socias registradas.")
        return

    opciones = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("👩 Seleccione una socia", opciones.keys())
    id_socia = opciones[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ PRÉSTAMO ACTIVO
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))

    prestamo = cursor.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene un préstamo activo.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    monto = Decimal(prestamo["Monto prestado"])
    interes_total = Decimal(prestamo["Interes_total"])
    cuotas = int(prestamo["Cuotas"])
    saldo_pendiente = Decimal(prestamo["Saldo pendiente"])

    total_a_pagar = monto + interes_total
    cuota_fija = (total_a_pagar / cuotas).quantize(Decimal("0.01"))
    interes_por_cuota = (interes_total / cuotas).quantize(Decimal("0.01"))
    capital_por_cuota = (cuota_fija - interes_por_cuota).quantize(Decimal("0.01"))

    # ---------------------------------------------------------
    # 3️⃣ MOSTRAR DETALLE
    # ---------------------------------------------------------
    st.subheader("📄 Detalle del préstamo")

    detalles = {
        "ID Préstamo": id_prestamo,
        "Monto prestado": f"${monto}",
        "Interés total": f"${interes_total}",
        "Total a pagar": f"${total_a_pagar}",
        "Número de cuotas": cuotas,
        "Cuota fija": f"${cuota_fija}",
        "Interés por cuota": f"${interes_por_cuota}",
        "Capital por cuota": f"${capital_por_cuota}",
        "Saldo pendiente": f"${saldo_pendiente}"
    }

    st.table(pd.DataFrame(detalles.items(), columns=["Detalle", "Valor"]))

    # ---------------------------------------------------------
    # 4️⃣ FORMULARIO DE PAGO
    # ---------------------------------------------------------
    fecha_pago_raw = st.date_input("📅 Fecha del pago", date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    if st.button("💵 Registrar pago"):

        try:
            # ---------------------------------------------------------
            # 5️⃣ CALCULAR NUEVO SALDO
            # ---------------------------------------------------------
            nuevo_saldo = saldo_pendiente - cuota_fija
            if nuevo_saldo < 0:
                nuevo_saldo = Decimal("0.00")

            # ---------------------------------------------------------
            # 6️⃣ Registrar movimiento en CAJA
            # ---------------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_pago)

            registrar_movimiento(
                id_caja=id_caja,
                tipo="Ingreso",
                categoria=f"Pago préstamo – {socia_sel}",
                monto=float(cuota_fija)
            )

            # ---------------------------------------------------------
            # 7️⃣ INSERTAR REGISTRO EN Pago_del_prestamo
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO Pago_del_prestamo(
                    `Fecha_pago`,
                    `Monto_abonado`,
                    `Interes_pagado`,
                    `Capital_pagado`,
                    `Saldo_restante`,
                    Id_Prestamo,
                    Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                fecha_pago,
                float(cuota_fija),
                float(interes_por_cuota),
                float(capital_por_cuota),
                float(nuevo_saldo),
                id_prestamo,
                id_caja
            ))

            # ---------------------------------------------------------
            # 8️⃣ ACTUALIZAR PRÉSTAMO
            # ---------------------------------------------------------
            estado = "pagado" if nuevo_saldo == 0 else "activo"

            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=%s,
                    Estado_del_prestamo=%s
                WHERE Id_Préstamo=%s
            """, (nuevo_saldo, estado, id_prestamo))

            con.commit()

            st.success("✔ Pago registrado correctamente.")
            st.info(f"Nuevo saldo pendiente: ${nuevo_saldo}")

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
        st.dataframe(pd.DataFrame(pagos), hide_index=True)
    else:
        st.info("Aún no hay pagos registrados.")

    cursor.close()
    con.close()
