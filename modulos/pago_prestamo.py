import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()

    # ==========================
    # 1️⃣ SOCIAS
    # ==========================
    cur = con.cursor()
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()
    cur.close()

    dict_socias = {f"{id_s}-{nombre}": id_s for id_s, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ==========================
    # 2️⃣ PRÉSTAMOS ACTIVOS
    # ==========================
    cur = con.cursor()
    cur.execute("""
        SELECT 
            Id_Préstamo,
            `Fecha del préstamo`,
            `Monto prestado`,
            `Saldo pendiente`,
            Cuotas,
            `Tasa de interes`,
            Plazo
        FROM Prestamo
        WHERE Id_Socia = %s AND Estado_del_prestamo = 'activo'
    """, (id_socia,))
    prestamos = cur.fetchall()
    cur.close()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    opciones = {f"ID {p[0]} | Prestado: ${p[2]} | Saldo: ${p[3]}": p[0] for p in prestamos}
    prestamo_sel = st.selectbox("📌 Seleccione el préstamo:", opciones.keys())
    id_prestamo = opciones[prestamo_sel]

    # ==========================
    # 3️⃣ OBTENER DATOS DEL PRÉSTAMO
    # ==========================
    cur = con.cursor()
    cur.execute("""
        SELECT 
            `Fecha del préstamo`,
            `Monto prestado`,
            `Saldo pendiente`,
            `Tasa de interes`,
            Plazo,
            Cuotas
        FROM Prestamo
        WHERE Id_Préstamo = %s
    """, (id_prestamo,))
    fecha_prestamo, monto_prestado, saldo_pendiente, tasa, plazo, cuotas = cur.fetchone()
    cur.close()

    st.subheader("📄 Información del préstamo")
    st.write(f"**Fecha del préstamo:** {fecha_prestamo}")
    st.write(f"**Monto prestado:** ${monto_prestado}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")
    st.write(f"**Tasa de interés:** {tasa}%")
    st.write(f"**Plazo:** {plazo} meses")
    st.write(f"**Cuotas:** {cuotas}")

    # ==========================
    # 4️⃣ REGISTRO DE PAGO
    # ==========================
    st.markdown("---")
    fecha_pago_raw = st.date_input("📅 Fecha del pago", value=date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.01, step=0.50)

    if st.button("💾 Registrar pago"):

        try:
            # ==========================
            # 5️⃣ ACTUALIZAR CAJA
            # ==========================
            cur = con.cursor()
            cur.execute("""
                SELECT Saldo_actual
                FROM Caja
                ORDER BY Id_Caja DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            saldo_actual = row[0] if row else 0
            cur.close()

            nuevo_saldo_caja = saldo_actual + float(monto_abonado)

            cur = con.cursor()
            cur.execute("""
                INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, 1, 2, %s)
            """, (
                f"Pago de préstamo (Socia {id_socia})",
                monto_abonado,
                nuevo_saldo_caja,
                fecha_pago
            ))
            id_caja = cur.lastrowid
            cur.close()

            # ==========================
            # 6️⃣ REGISTRAR PAGO EN Pago_del_prestamo
            # ==========================
            nuevo_saldo_prestamo = saldo_pendiente - float(monto_abonado)
            if nuevo_saldo_prestamo < 0:
                nuevo_saldo_prestamo = 0

            cur = con.cursor()
            cur.execute("""
                INSERT INTO Pago_del_prestamo
                (`Fecha_de_pago`, `Monto_abonado`, `Interes_pagado`, `Capital_pagado`,
                 `Saldo_restante`, `Id_Prestamo`, `Id_Caja`)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (
                fecha_pago,
                monto_abonado,
                0,        # Interés pagado
                0,        # Capital pagado
                nuevo_saldo_prestamo,
                id_prestamo,
                id_caja
            ))
            cur.close()

            # ==========================
            # 7️⃣ ACTUALIZAR PRÉSTAMO
            # ==========================
            estado = "cancelado" if nuevo_saldo_prestamo == 0 else "activo"

            cur = con.cursor()
            cur.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente`=%s,
                    Estado_del_prestamo=%s
                WHERE Id_Préstamo=%s
            """, (nuevo_saldo_prestamo, estado, id_prestamo))
            cur.close()

            con.commit()

            st.success("✅ Pago registrado correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")

    # ==========================
    # 8️⃣ HISTORIAL DE PAGOS
    # ==========================
    st.subheader("📜 Historial de pagos")

    cur = con.cursor()
    cur.execute("""
        SELECT *
        FROM Pago_del_prestamo
        WHERE Id_Prestamo=%s
        ORDER BY Id_Pago ASC
    """, (id_prestamo,))
    pagos = cur.fetchall()
    cur.close()

    if pagos:
        import pandas as pd
        df = pd.DataFrame(pagos)
        st.dataframe(df)
    else:
        st.info("No tiene pagos registrados.")

    con.close()
