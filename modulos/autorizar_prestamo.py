import streamlit as st
from datetime import date, datetime, timedelta
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento

# 🔗 REGLAS INTERNAS
from modulos.reglas_utils import obtener_reglas


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    # ============================================================
    # 🔗 Cargar reglas internas
    # ============================================================
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ No existen reglas internas registradas.")
        return

    # REGLAS CORRECTAS
    prestamo_maximo = float(reglas.get("prestamo_maximo", 0))  # debe ser 100 en BD
    interes_por_10 = float(reglas.get("interes_por_10", 6))    # interés fijo 6%
    plazo_maximo = int(reglas.get("plazo_maximo", 12))

    # ============================================================
    # CONEXIÓN
    # ============================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # SOCIAS
    # ============================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ============================================================
    # FORMULARIO
    # ============================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input(
            "📅 Fecha del préstamo",
            date.today()
        ).strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia", list(lista_socias.keys()))
        id_socia = lista_socias[socia_sel]

        # ============================================================
        # Recuperar ahorro total de la socia
        # ============================================================
        cursor.execute("""
            SELECT `Saldo acumulado`
            FROM Ahorro
            WHERE Id_Socia=%s
            ORDER BY Id_Ahorro DESC
            LIMIT 1
        """, (id_socia,))
        row = cursor.fetchone()
        ahorro_total = Decimal(row["Saldo acumulado"]) if row else Decimal("0.00")

        # ============================================================
        # Nuevo límite real del préstamo
        # ============================================================
        limite_real = float(min(ahorro_total, Decimal(prestamo_maximo)))

        monto = st.number_input(
            "💵 Monto prestado ($):",
            min_value=1.0,
            max_value=limite_real,   # ← límite real corregido
            step=1.0,
            help=f"Monto máximo permitido según ahorro y reglas: ${limite_real}"
        )

        # ============================================================
        # Interés FIJO según reglas internas (6%)
        # ============================================================
        tasa = st.number_input(
            "📈 Interés (%)",
            min_value=0.0,
            max_value=100.0,
            value=interes_por_10,   # ← SIEMPRE 6%
            disabled=True           # ← NO EDITABLE
        )

        plazo = st.number_input(
            "🗓 Plazo (meses):",
            min_value=1,
            max_value=plazo_maximo
        )

        cuotas = st.number_input(
            "📑 Número de cuotas",
            min_value=1
        )

        firma = st.text_input("✍️ Firma directiva")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ============================================================
    # DETENER SI NO ENVÍA
    # ============================================================
    if not enviar:
        return

    # ============================================================
    # VALIDACIÓN – Préstamos activos
    # ============================================================
    cursor.execute("""
        SELECT COUNT(*) AS activos
        FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    if cursor.fetchone()["activos"] > 0:
        st.error("❌ La socia ya tiene un préstamo activo.")
        return

    # ============================================================
    # VALIDACIÓN – Ahorro suficiente
    # ============================================================
    if Decimal(monto) > ahorro_total:
        st.error(f"❌ Ahorro insuficiente. Tiene ${ahorro_total}.")
        return

    # ============================================================
    # VALIDACIÓN – Caja suficiente
    # ============================================================
    id_caja = obtener_o_crear_reunion(fecha_prestamo)

    cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    saldo_caja = Decimal(cursor.fetchone()["saldo_final"])

    if Decimal(monto) > saldo_caja:
        st.error(f"❌ Saldo insuficiente en caja. Disponible: ${saldo_caja}.")
        return

    # ============================================================
    # CÁLCULOS
    # ============================================================
    interes_total = Decimal(monto) * (Decimal(tasa) / 100)
    total_pagar = Decimal(monto) + interes_total

    # ============================================================
    # REGISTRAR PRÉSTAMO
    # ============================================================
    cursor.execute("""
        INSERT INTO Prestamo(
            `Fecha del préstamo`, `Monto prestado`, `Interes_total`,
            `Tasa de interes`, `Plazo`, `Cuotas`, `Saldo pendiente`,
            Estado_del_prestamo, Id_Grupo, Id_Socia, Id_Caja
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,'activo',1,%s,%s)
    """, (
        fecha_prestamo, monto, interes_total,
        tasa, plazo, cuotas, total_pagar,
        id_socia, id_caja
    ))

    id_prestamo_generado = cursor.lastrowid

    # ============================================================
    # DESCONTAR AHORRO
    # ============================================================
    nuevo_ahorro = ahorro_total - Decimal(monto)

    cursor.execute("""
        INSERT INTO Ahorro(
            `Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
            `Comprobante digital`, `Saldo acumulado`, Id_Socia
        )
        VALUES (%s,%s,'Descuento préstamo','---',%s,%s)
    """, (
        fecha_prestamo,
        -Decimal(monto),
        nuevo_ahorro,
        id_socia
    ))

    # ============================================================
    # RESTAR DE CAJA
    # ============================================================
    registrar_movimiento(
        id_caja=id_caja,
        tipo="Egreso",
        categoria=f"Préstamo otorgado – {socia_sel}",
        monto=float(monto)
    )

    # ============================================================
    # CUOTAS (cada 15 días)
    # ============================================================
    valor_cuota = total_pagar / Decimal(cuotas)
    fecha_base = datetime.strptime(fecha_prestamo, "%Y-%m-%d")

    for n in range(1, cuotas + 1):
        fecha_cuota = fecha_base + timedelta(days=15 * n)
        cursor.execute("""
            INSERT INTO Cuotas_prestamo
            (Id_Prestamo, Numero_cuota, Fecha_programada, Monto_cuota, Estado)
            VALUES (%s,%s,%s,%s,'pendiente')
        """, (
            id_prestamo_generado, n,
            fecha_cuota.strftime("%Y-%m-%d"),
            round(valor_cuota, 2)
        ))

    con.commit()

    st.success("✔ Préstamo autorizado correctamente.")
