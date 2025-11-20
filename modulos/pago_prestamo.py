import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    dict_socias = {f"{id_s}-{nombre}": id_s for id_s, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ PRÉSTAMOS ACTIVOS
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT 
            Id_Préstamo,
            `Fecha del préstamo`,
            `Monto prestado`,
            `Saldo pendiente`,
            Cuotas,
            `Tasa de interes`,
            Plazo
        FROM Prestamo
        WHERE Id_Socia = %s AND LOWER(Estado_del_prestamo) = 'activo'
    """, (id_socia,))

    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    opciones = {f"ID {p[0]} | Prestado: ${p[2]} | Saldo: ${p[3]}": p[0] for p in prestamos}
    prestamo_sel = st.selectbox("📌 Seleccione el préstamo:", opciones.keys())
    id_prestamo = opciones[prestamo_sel]

    # ---------------------------------------------------------
    # 3️⃣ OBTENER DATOS DEL PRÉSTAMO
    # ---------------------------------------------------------
    cursor.execute("""
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

    fecha_prestamo, monto_prestado, saldo_pendiente, tasa, plazo, cuotas = cursor.fetchone()

    st.subheader("📄 Información del préstamo")
    st.write(f"**Fecha del préstamo:** {fecha_prestamo}")
    st.write(f"**Monto prestado:** ${monto_prestado}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")
    st.write(f"**Tasa de interés:** {tasa}%")
    st.write(f"**Plazo:** {plazo} meses")
    st.write(f"**Cuotas:** {cuotas}")

    # ---------------------------------------------------------
    # 4️⃣ REGISTRO DE PAGO
    # ---------------------------------------------------------
    st.markdown("---")
    fecha_pago_raw = st.date_input("📅 Fecha del pago", value=date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.01, step=0.50)

    if st.button("💾 Registrar pago"):

        try:
            # ---------------------------------------------------------
            # 5️⃣ INSERTAR MOVIMIENTO EN CAJA
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
                INSERT INTO Caja (Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento, Fecha)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                f"Pago de préstamo (socia {id_socia})",
                monto_abonado,
                nuevo_saldo_caja,
                1,
                2,  # INGRESO
                fecha_pago
            ))

            id_caja = cursor.lastrowid

            # ---------------------------------------------------------
            # 6️⃣ REGISTRAR EL PAGO EN LA TABLA (NOMBRES CON ESPACIOS)
            # ---------------------------------------------------------
            nuevo_saldo_prestamo = saldo_pendiente - float(monto_abonado)
            if nuevo_saldo_prestamo < 0:
                nuevo_saldo_prestamo = 0

            cursor.execute("""
                INSERT INTO `Pago del prestamo`
                (`Fecha de pago`, `Monto abonado`, `Interés pagado`, `Capital pagado`, `Saldo restante`, Id_Préstamo, Id_Caja)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                fecha_pago,
                monto_abonado,
                0,  # interés
                0,  # capital
                nuevo_saldo_prestamo,
                id_prestamo,
                id_caja
            ))

            # ---------------------------------------------------------
            # 7️⃣ ACTUALIZAR PRÉSTAMO
            # ---------------------------------------------------------
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente` = %s,
                    Estado_del_prestamo = CASE 
                        WHEN %s = 0 THEN 'cancelado' 
                        ELSE 'activo' 
                    END
                WHERE Id_Préstamo = %s
            """, (nuevo_saldo_prestamo, nuevo_saldo_prestamo, id_prestamo))

            con.commit()
            st.success("✅ Pago registrado y CAJA actualizada.")

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")
