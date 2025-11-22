import streamlit as st
import pandas as pd
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def pago_prestamo():

    st.title("💰 Pago de préstamo")

    con = obtener_conexion()

    # ======================================================
    # 1️⃣ SOCIAS
    # ======================================================
    cur1 = con.cursor(dictionary=True)
    cur1.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur1.fetchall()
    cur1.close()

    if not socias:
        st.warning("No hay socias registradas.")
        return

    opciones = {f"{s['Id_Socia']} - {s['Nombre']}": s['Id_Socia'] for s in socias}
    socia_sel = st.selectbox("👩 Socia:", opciones.keys())
    id_socia = opciones[socia_sel]

    # ======================================================
    # 2️⃣ PRÉSTAMO ACTIVO
    # ======================================================
    cur2 = con.cursor(dictionary=True)
    cur2.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    prestamo = cur2.fetchone()
    cur2.close()

    if not prestamo:
        st.info("La socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    monto = prestamo["Monto prestado"]
    interes_total = prestamo["Interes_total"]
    cuotas = prestamo["Cuotas"]
    saldo_pendiente = prestamo["Saldo pendiente"]

    total_a_pagar = monto + interes_total
    cuota_fija = round(total_a_pagar / cuotas, 2)
    interes_por_cuota = round(interes_total / cuotas, 2)

    # ======================================================
    # 3️⃣ MOSTRAR DETALLE
    # ======================================================
    st.subheader("📄 Detalle del préstamo")

    info = {
        "Monto prestado": f"${monto:.2f}",
        "Interés total": f"${interes_total:.2f}",
        "Cuotas": cuotas,
        "Cuota fija": f"${cuota_fija:.2f}",
        "Interés por cuota": f"${interes_por_cuota:.2f}",
        "Saldo pendiente": f"${saldo_pendiente:.2f}"
    }

    st.table(pd.DataFrame(info.items(), columns=["Detalle", "Valor"]))

    # ======================================================
    # 4️⃣ FORMULARIO DE PAGO
    # ======================================================
    fecha_pago_raw = st.date_input("📅 Fecha del pago", date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    if st.button("💵 Registrar pago"):

        pago_total = cuota_fija
        capital_pagado = round(pago_total - interes_por_cuota, 2)
        nuevo_saldo = round(saldo_pendiente - pago_total, 2)
        if nuevo_saldo < 0:
            nuevo_saldo = 0

        # ======================================================
        # 5️⃣ MOVIMIENTO EN CAJA
        # ======================================================
        id_caja = obtener_o_crear_reunion(fecha_pago)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Pago préstamo – {socia_sel}",
            monto=pago_total
        )

        # ======================================================
        # 6️⃣ REGISTRAR EN TABLA Pago_del_prestamo
        # ======================================================
        cur3 = con.cursor()
        cur3.execute("""
            INSERT INTO Pago_del_prestamo(
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
            pago_total,
            interes_por_cuota,
            capital_pagado,
            nuevo_saldo,
            id_prestamo,
            id_caja
        ))
        cur3.close()

        # ======================================================
        # 7️⃣ ACTUALIZAR PRÉSTAMO
        # ======================================================
        cur4 = con.cursor()
        cur4.execute("""
            UPDATE Prestamo
            SET `Saldo pendiente`=%s,
                Estado_del_prestamo = CASE 
                    WHEN %s = 0 THEN 'cancelado'
                    ELSE 'activo'
                END
            WHERE Id_Préstamo=%s
        """, (nuevo_saldo, nuevo_saldo, id_prestamo))
        cur4.close()

        con.commit()
        st.success("✔ Pago registrado correctamente.")
        st.rerun()

    # ======================================================
    # 8️⃣ HISTORIAL (USANDO OTRO CURSOR)
    # ======================================================
    st.subheader("📜 Historial de pagos")

    cur5 = con.cursor(dictionary=True)
    cur5.execute("""
        SELECT *
        FROM Pago_del_prestamo
        WHERE Id_Prestamo=%s
        ORDER BY Id_Pago ASC
    """, (id_prestamo,))
    pagos = cur5.fetchall()
    cur5.close()

    if pagos:
        st.dataframe(pd.DataFrame(pagos), hide_index=True)
    else:
        st.info("La socia aún no tiene pagos registrados.")

    con.close()
