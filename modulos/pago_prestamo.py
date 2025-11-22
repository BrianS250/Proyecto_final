import streamlit as st
from datetime import date
import pandas as pd

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}
    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ PRÉSTAMO ACTIVO
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND LOWER(Estado_del_prestamo)='activo'
    """, (id_socia,))
    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    prestamo = prestamos[0]
    id_prestamo = prestamo["Id_Préstamo"]
    saldo_pendiente = float(prestamo["Saldo pendiente"])

    st.subheader("📄 Información del préstamo")
    st.write(f"**ID Préstamo:** {id_prestamo}")
    st.write(f"**Monto prestado:** ${prestamo['Monto prestado']}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")

    # ---------------------------------------------------------
    # 3️⃣ FORM DE PAGO
    # ---------------------------------------------------------
    fecha_pago = st.date_input("📅 Fecha del pago", date.today()).strftime("%Y-%m-%d")
    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.50, step=0.50)

    if st.button("💾 Registrar pago"):

        try:
            # ---------------------------------------------------------
            # 4️⃣ Registrar movimiento correcto EN caja_reunion
            # ---------------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_pago)

            registrar_movimiento(
                id_caja=id_caja,
                tipo="Ingreso",
                categoria=f"Pago préstamo – {socia_sel}",
                monto=monto_abonado
            )

            # ---------------------------------------------------------
            # 5️⃣ INSERTAR REGISTRO DE PAGO EN Pago_del_prestamo
            # ---------------------------------------------------------
            nuevo_saldo_prestamo = saldo_pendiente - monto_abonado
            if nuevo_saldo_prestamo < 0:
                nuevo_saldo_prestamo = 0

            cursor.execute("""
                INSERT INTO Pago_del_prestamo
                (`Fecha de pago`, `Monto abonado`, `Interés pagado`,
                 `Capital pagado`, `Saldo restante`, Id_Préstamo, Id_Caja)
                VALUES (%s,%s,0,0,%s,%s,%s)
            """, (
                fecha_pago,
                monto_abonado,
                nuevo_saldo_prestamo,
                id_prestamo,
                id_caja
            ))

            # ---------------------------------------------------------
            # 6️⃣ Actualizar préstamo
            # ---------------------------------------------------------
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=%s,
                    Estado_del_prestamo = CASE
                        WHEN %s = 0 THEN 'pagado'
                        ELSE 'activo'
                    END
                WHERE Id_Préstamo=%s
            """, (nuevo_saldo_prestamo, nuevo_saldo_prestamo, id_prestamo))

            con.commit()

            st.success("✔ Pago registrado y sumado a caja correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")

    # ---------------------------------------------------------
    # 7️⃣ HISTORIAL DE PAGOS
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT *
        FROM Pago_del_prestamo
        WHERE Id_Préstamo=%s
        ORDER BY Id_Pago ASC
    """, (id_prestamo,))
    pagos = cursor.fetchall()

    if pagos:
        st.subheader("📜 Histórico de pagos")
        st.dataframe(pd.DataFrame(pagos), hide_index=True)
