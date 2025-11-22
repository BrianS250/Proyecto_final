import streamlit as st
from datetime import date, timedelta
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ======================================================
    # SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_raw = st.date_input("📅 Fecha del préstamo", date.today())
        fecha_prestamo = fecha_raw.strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[socia_sel]

        monto = Decimal(str(st.number_input("💵 Monto prestado ($):", min_value=1.0, step=1.0)))
        tasa = Decimal(str(st.number_input("📈 Tasa de interés (%)", min_value=1.0, step=1.0)))
        plazo = int(st.number_input("🗓 Plazo (meses):", min_value=1))
        cuotas = int(st.number_input("📑 Número de cuotas:", min_value=1))
        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    if not enviar:
        return

    # ======================================================
    # VALIDACIONES
    # ======================================================

    # 1. Préstamo activo
    cursor.execute("""
        SELECT COUNT(*) AS activos
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    if cursor.fetchone()["activos"] > 0:
        st.error("❌ La socia ya tiene un préstamo activo.")
        return

    # 2. Ahorro
    cursor.execute("""
        SELECT `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia=%s
        ORDER BY Id_Ahorro DESC
        LIMIT 1
    """, (id_socia,))
    row = cursor.fetchone()
    ahorro = Decimal(str(row["Saldo acumulado"])) if row else Decimal("0.00")

    if ahorro < monto:
        st.error(f"❌ Ahorro insuficiente: solo tiene ${ahorro:.2f}")
        return

    # 3. Caja
    id_caja = obtener_o_crear_reunion(fecha_prestamo)
    cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    saldo_caja = Decimal(str(cursor.fetchone()["saldo_final"]))

    if monto > saldo_caja:
        st.error(f"❌ Fondos insuficientes en caja. Saldo actual: ${saldo_caja:.2f}")
        return

    # ======================================================
    # CÁLCULOS
    # ======================================================

    interes_total = monto * (tasa / 100)
    total_a_pagar = monto + interes_total
    cuota_fija = (total_a_pagar / cuotas).quantize(Decimal("0.01"))

    # Fechas de pago
    fechas = [
        (fecha_raw + timedelta(days=15 * (i + 1))).strftime("%Y-%m-%d")
        for i in range(cuotas)
    ]

    # ======================================================
    # INSERTAR PRÉSTAMO
    # ======================================================
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
        total_a_pagar,
        id_socia,
        id_caja
    ))

    # EGRESO DE CAJA
    registrar_movimiento(
        id_caja=id_caja,
        tipo="Egreso",
        categoria=f"Préstamo otorgado – {socia_sel}",
        monto=float(monto)
    )

    con.commit()

    st.success("✔ Préstamo autorizado correctamente y descontado de caja.")

    # ======================================================
    # RESUMEN PROFESIONAL
    # ======================================================

    st.subheader("📄 Resumen del préstamo")

    st.table({
        "Dato": [
            "Fecha del préstamo",
            "Socia",
            "Monto prestado",
            "Interés total",
            "Total a pagar",
            "Plazo (meses)",
            "Número de cuotas",
            "Cuota fija"
        ],
        "Valor": [
            fecha_prestamo,
            socia_sel,
            f"${monto:.2f}",
            f"${interes_total:.2f}",
            f"${total_a_pagar:.2f}",
            plazo,
            cuotas,
            f"${cuota_fija:.2f}",
        ]
    })

    st.subheader("📅 Calendario de pagos")

    st.table({
        "Cuota Nº": list(range(1, cuotas + 1)),
        "Fecha de pago": fechas,
        "Monto": [f"${cuota_fija:.2f}"] * cuotas
    })
