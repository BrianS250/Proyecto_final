import streamlit as st
from datetime import date, datetime, timedelta
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
#     AUTORIZAR PRÉSTAMO — SISTEMA CVX (VERSIÓN FINAL)
# ============================================================
def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # 1️⃣ OBTENER SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ======================================================
    # 2️⃣ FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today()).strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[socia_sel]

        monto = st.number_input("💵 Monto prestado ($):", min_value=1.0, step=1.0)
        tasa = st.number_input("📈 Tasa de interés (%)", min_value=1.0, step=1.0)
        plazo = st.number_input("🗓 Plazo (meses):", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas:", min_value=1)
        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # 3️⃣ PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # -----------------------------------------------
        # VALIDACIÓN 1 — PRÉSTAMO ACTIVO
        # -----------------------------------------------
        cursor.execute("""
            SELECT COUNT(*) AS activos
            FROM Prestamo
            WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
        """, (id_socia,))
        activos = cursor.fetchone()["activos"]

        if activos > 0:
            st.error("❌ La socia ya tiene un préstamo activo.")
            return

        # -----------------------------------------------
        # VALIDACIÓN 2 — AHORRO TOTAL
        # -----------------------------------------------
        cursor.execute("""
            SELECT `Saldo acumulado`
            FROM Ahorro
            WHERE Id_Socia=%s
            ORDER BY Id_Ahorro DESC
            LIMIT 1
        """, (id_socia,))

        row = cursor.fetchone()
        ahorro_total = Decimal(row["Saldo acumulado"]) if row else Decimal("0.00")

        if ahorro_total < Decimal(monto):
            st.error(
                f"❌ La socia solo tiene ${ahorro_total:.2f} de ahorro. "
                f"No puede solicitar un préstamo de ${monto:.2f}."
            )
            return

        # -----------------------------------------------
        # VALIDACIÓN 3 — SALDO DE CAJA REUNIÓN
        # -----------------------------------------------
        id_caja = obtener_o_crear_reunion(fecha_prestamo)

        cursor.execute("""
            SELECT saldo_final FROM caja_reunion WHERE id_caja=%s
        """, (id_caja,))
        saldo_caja = Decimal(cursor.fetchone()["saldo_final"])

        if Decimal(monto) > saldo_caja:
            st.error(f"❌ Saldo insuficiente en caja. Saldo actual: ${saldo_caja:.2f}")
            return

        # -----------------------------------------------
        # CALCULO DEL INTERÉS TOTAL
        # -----------------------------------------------
        interes_total = Decimal(monto) * (Decimal(tasa) / 100)
        total_pagar = Decimal(monto) + interes_total

        # -----------------------------------------------
        # 4️⃣ REGISTRAR PRÉSTAMO
        # -----------------------------------------------
        cursor.execute("""
            INSERT INTO Prestamo(
                `Fecha del préstamo`,
                `Monto prestado`,
                `Interes_total`,
                `Tasa de interes`,
                `Plazo`,
                `Cuotas`,
                `Saldo pendiente`,
                Estado_del_prestamo,
                Id_Grupo,
                Id_Socia,
                Id_Caja
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,'activo',1,%s,%s)
        """, (
            fecha_prestamo,
            monto,
            interes_total,
            tasa,
            plazo,
            cuotas,
            total_pagar,
            id_socia,
            id_caja
        ))

        id_prestamo_generado = cursor.lastrowid

        # -----------------------------------------------
        # 5️⃣ DESCONTAR AHORRO DE LA SOCIA
        # -----------------------------------------------
        nuevo_ahorro = ahorro_total - Decimal(monto)

        cursor.execute("""
            INSERT INTO Ahorro
            (Fecha_del_aporte, Monto, `Tipo de aporte`, `Comprobante digital`, `Saldo acumulado`,
             Id_Socia, Id_Reunion, Id_Grupo, Id_Caja)
            VALUES (%s, %s, 'Descuento préstamo', '---', %s, %s, NULL, 1, NULL)
        """, (
            fecha_prestamo,
            -Decimal(monto),
            nuevo_ahorro,
            id_socia
        ))

        # -----------------------------------------------
        # 6️⃣ REGISTRAR EGRESO EN CAJA
        # -----------------------------------------------
        registrar_movimiento(
            id_caja=id_caja,
            tipo="Egreso",
            categoria=f"Préstamo otorgado – {socia_sel}",
            monto=monto
        )

        # -----------------------------------------------
        # 7️⃣ GENERAR CUOTAS AUTOMÁTICAS
        # -----------------------------------------------
        valor_cuota = total_pagar / Decimal(cuotas)
        fecha_base = datetime.strptime(fecha_prestamo, "%Y-%m-%d")

        for n in range(1, cuotas + 1):
            fecha_cuota = fecha_base + timedelta(days=15 * n)

            cursor.execute("""
                INSERT INTO Cuotas_prestamo
                (Id_Prestamo, Numero_cuota, Fecha_programada, Monto_cuota, Estado)
                VALUES (%s, %s, %s, %s, 'pendiente')
            """, (
                id_prestamo_generado,
                n,
                fecha_cuota.strftime("%Y-%m-%d"),
                round(valor_cuota, 2)
            ))

        con.commit()

        # -----------------------------------------------
        # 8️⃣ RESUMEN DEL PRÉSTAMO
        # -----------------------------------------------
        st.success("✔ Préstamo autorizado correctamente y descontado de caja y ahorro.")

        st.subheader("📘 Resumen del préstamo")

        st.write(f"**Socia:** {socia_sel}")
        st.write(f"**Monto prestado:** ${monto}")
        st.write(f"**Interés total:** ${interes_total:.2f}")
        st.write(f"**Total a pagar:** ${total_pagar:.2f}")
        st.write(f"**Cuotas:** {cuotas}")
        st.write(f"**Valor por cuota:** ${round(valor_cuota, 2)}")
        st.write("**📅 Calendario de pagos:**")

        for n in range(1, cuotas + 1):
            fecha_cuota = (fecha_base + timedelta(days=15 * n)).strftime("%Y-%m-%d")
            st.write(f"➡ Cuota #{n}: {fecha_cuota} — ${round(valor_cuota, 2)}")
