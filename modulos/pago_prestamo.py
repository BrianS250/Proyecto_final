import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS CON ID
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

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
        WHERE Id_Socia = %s AND TRIM(Estado_del_prestamo) = 'activo'
    """, (id_socia,))

    prestamos = cursor.fetchall()

    if not prestamos:
        st.info("Esta socia no tiene préstamos activos.")
        return

    opciones = {
        f"ID {p[0]} | Prestado: ${p[2]} | Saldo: ${p[3]}": p[0] for p in prestamos
    }

    prestamo_sel = st.selectbox("📌 Seleccione el préstamo:", list(opciones.keys()))
    id_prestamo = opciones[prestamo_sel]

    # ---------------------------------------------------------
    # 3️⃣ Obtener datos del préstamo seleccionado
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
    # 4️⃣ REGISTRAR PAGO
    # ---------------------------------------------------------
    st.markdown("---")
    st.header("🧾 Registrar pago")

    fecha_pago_raw = st.date_input("📅 Fecha del pago:", value=date.today())
    fecha_pago = fecha_pago_raw.strftime("%Y-%m-%d")

    monto_abonado = st.number_input("💵 Monto abonado ($):", min_value=0.01, step=0.50)

    if st.button("💾 Registrar pago"):

        try:
            nuevo_saldo = saldo_pendiente - float(monto_abonado)
            if nuevo_saldo < 0:
                nuevo_saldo = 0

            # ---------------------------------------------------------
            # 5️⃣ INSERTAR EN PAGO DEL PRESTAMO  (Nombres exactos)
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO `Pago del prestamo`
                (`Fecha de pago`, `Monto abonado`, `Interés pagado`, `Capital pagado`,
                 `Saldo restante`, `Id_Préstamo`, Id_Caja)
                VALUES (%s, %s, 0, 0, %s, %s, 1)
            """, (fecha_pago, monto_abonado, nuevo_saldo, id_prestamo))

            # ---------------------------------------------------------
            # 6️⃣ ACTUALIZAR PRÉSTAMO
            # ---------------------------------------------------------
            cursor.execute("""
                UPDATE Prestamo
                SET `Saldo pendiente` = %s,
                    Estado_del_prestamo = CASE WHEN %s = 0 THEN 'cancelado' ELSE 'activo' END
                WHERE Id_Préstamo = %s
            """, (nuevo_saldo, nuevo_saldo, id_prestamo))

            con.commit()
            st.success("✅ Pago registrado correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")
