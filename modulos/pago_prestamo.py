import streamlit as st
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import registrar_movimiento, obtener_o_crear_reunion
from modulos.reglas_utils import obtener_reglas


def pago_prestamo():

    st.header("💵 Registro de pagos de préstamos")

    # ============================================================
    # 🔗 Cargar reglas internas
    # ============================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No hay reglas internas registradas. Configúralas primero.")
        return

    multa_mora = Decimal(str(reglas.get("multa_mora", 0)))

    con = obtener_conexion()
    cur = con.cursor(dictionary=True)

    # ============================================================
    # SOCIAS
    # ============================================================
    cur.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cur.fetchall()

    dict_socias = {
        f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] 
        for s in socias
    }

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ============================================================
    # PRÉSTAMO ACTIVO
    # ============================================================
    cur.execute("""
        SELECT *
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
        LIMIT 1
    """, (id_socia,))
    prestamo = cur.fetchone()

    if not prestamo:
        st.info("Esta socia no tiene préstamos activos.")
        return

    id_prestamo = prestamo["Id_Préstamo"]
    saldo_pendiente = Decimal(prestamo["Saldo pendiente"])

    # ============================================================
    # CALCULAR INTERÉS TOTAL REAL (NO EXISTE EN LA TABLA)
    # ============================================================
    monto_prestado = Decimal(prestamo["Monto prestado"])
    tasa = Decimal(prestamo["Tasa de interes"])
    interes_total = round(monto_prestado * tasa / Decimal(100), 2)

    # ============================================================
    # MOSTRAR INFORMACIÓN DEL PRÉSTAMO
    # ============================================================
    st.subheader("📄 Información del préstamo")
    st.write(f"**ID Préstamo:** {id_prestamo}")
    st.write(f"**Monto prestado:** ${monto_prestado}")
    st.write(f"📈 **Interés total:** ${interes_total}")
    st.write(f"**Saldo pendiente:** ${saldo_pendiente}")
    st.write(f"**Cuotas:** {prestamo['Cuotas']}")

    st.divider()

    # ============================================================
    # CUOTAS PENDIENTES
    # ============================================================
    cur.execute("""
        SELECT *
        FROM Cuotas_prestamo
        WHERE Id_Prestamo=%s AND Estado='pendiente'
        ORDER BY Numero_cuota ASC
    """, (id_prestamo,))
    cuotas = cur.fetchall()

    if not cuotas:
        st.success("🎉 Todas las cuotas están pagadas.")
        return

    st.subheader("📅 Cuotas pendientes")

    opciones = {
        f"Cuota #{c['Numero_cuota']} — Fecha {c['Fecha_programada']} — ${c['Monto_cuota']}":
            c["Id_Cuota"]
        for c in cuotas
    }

    cuota_sel = st.selectbox("Seleccione la cuota a pagar:", opciones.keys())
    id_cuota = opciones[cuota_sel]

    fecha_pago = st.date_input("📅 Fecha del pago:", date.today()).strftime("%Y-%m-%d")

    # ============================================================
    # BOTÓN PRINCIPAL
    # ============================================================
    if st.button("💾 Registrar pago"):

        # Obtener datos de la cuota seleccionada
        cur.execute("SELECT * FROM Cuotas_prestamo WHERE Id_Cuota=%s", (id_cuota,))
        cuota = cur.fetchone()

        monto_cuota = Decimal(cuota["Monto_cuota"])
        fecha_programada = cuota["Fecha_programada"]

        fecha_programada_dt = date.fromisoformat(fecha_programada)
        fecha_pago_dt = date.fromisoformat(fecha_pago)

        atraso = fecha_pago_dt > fecha_programada_dt

        monto_total = monto_cuota

        # ============================================================
        # MULTA POR MORA
        # ============================================================
        if atraso and multa_mora > 0:

            monto_total += multa_mora
            st.warning(f"⚠ Pago atrasado: multa por mora de ${multa_mora}")

            # Registrar multa en tabla Multa
            cur.execute("""
                INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, 'A pagar', 2, %s)
            """, (multa_mora, fecha_pago, id_socia))

            # Registrar multa como ingreso de caja
            id_caja_multa = obtener_o_crear_reunion(fecha_pago)
            registrar_movimiento(
                id_caja=id_caja_multa,
                tipo="Ingreso",
                categoria=f"Multa por mora (Préstamo #{id_prestamo})",
                monto=float(multa_mora)
            )

        # ============================================================
        # PAGO DE CUOTA → CAJA
        # ============================================================
        id_caja = obtener_o_crear_reunion(fecha_pago)

        registrar_movimiento(
            id_caja=id_caja,
            tipo="Ingreso",
            categoria=f"Pago cuota préstamo {id_prestamo}",
            monto=float(monto_total)
        )

        # ============================================================
        # MARCAR CUOTA COMO PAGADA
        # ============================================================
        cur.execute("""
            UPDATE Cuotas_prestamo
            SET Estado='pagada', Fecha_pago=%s, Id_Caja=%s
            WHERE Id_Cuota=%s
        """, (fecha_pago, id_caja, id_cuota))

        # ============================================================
        # ACTUALIZAR SALDO DEL PRÉSTAMO
        # ============================================================
        nuevo_saldo = saldo_pendiente - monto_cuota

        if nuevo_saldo < 0:
            nuevo_saldo = Decimal("0.00")

        cur.execute("""
            UPDATE Prestamo
            SET `Saldo pendiente`=%s,
                Estado_del_prestamo =
                    CASE WHEN %s=0 THEN 'pagado' ELSE 'activo' END
            WHERE Id_Préstamo=%s
        """, (nuevo_saldo, nuevo_saldo, id_prestamo))

        con.commit()

        st.success("✔ Pago registrado correctamente.")
        st.rerun()
