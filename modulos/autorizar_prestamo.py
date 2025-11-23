import streamlit as st
from datetime import date, datetime, timedelta
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento
from modulos.reglas_utils import obtener_reglas


# ============================================================
# 🟩 AUTORIZAR PRÉSTAMO
# ============================================================
def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")

    # ============================================================
    # 🔹 Cargar reglas internas
    # ============================================================
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ No existen reglas internas registradas.")
        return

    prestamo_maximo = float(reglas["prestamo_maximo"])
    interes_por_10 = float(reglas["interes_por_10"])
    plazo_maximo = int(reglas["plazo_maximo"])

    # ============================================================
    # 🔹 Conexión
    # ============================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # ============================================================
    # 🔹 Socias
    # ============================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()
    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ============================================================
    # 🔹 Formulario
    # ============================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today()).strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia", list(lista_socias.keys()))
        id_socia = lista_socias[socia_sel]

        # ============================================================
        # 🔥 BLOQUEO TOTAL DE LETRAS / SÍMBOLOS / MÁS DE 2 DECIMALES
        # ============================================================
        monto_raw = st.text_input(
            "💵 Monto prestado ($):",
            placeholder=f"Máximo permitido: ${prestamo_maximo}"
        )

        # Mantener solo números y punto
        limpio = "".join([c for c in monto_raw if c.isdigit() or c == "."])

        # Solo un punto
        if limpio.count(".") > 1:
            partes = limpio.split(".")
            limpio = partes[0] + "." + "".join(partes[1:])

        # Máximo 2 decimales
        if "." in limpio:
            entero, decimal = limpio.split(".", 1)
            limpio = entero + "." + decimal[:2]

        # Reemplazo automático
        if limpio != monto_raw:
            st.warning("🔎 Se removieron caracteres no válidos.")
            st.experimental_rerun()

        try:
            monto = float(limpio) if limpio else 0.0
        except:
            monto = 0.0

        if monto > prestamo_maximo:
            st.error(f"❌ El monto máximo permitido es: ${prestamo_maximo}.")
            st.stop()

        # Interés automático según reglas
        tasa = interes_por_10

        plazo = st.number_input("🗓 Plazo (meses):", min_value=1, max_value=plazo_maximo)
        cuotas = st.number_input("📑 Número de cuotas", min_value=1)
        firma = st.text_input("✍️ Firma directiva")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    if not enviar:
        return

    # ============================================================
    # Validación — préstamo activo
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
    # Validación — ahorro suficiente
    # ============================================================
    cursor.execute("""
        SELECT `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia=%s
        ORDER BY Id_Ahorro DESC LIMIT 1
    """, (id_socia,))
    row = cursor.fetchone()
    ahorro_total = Decimal(row["Saldo acumulado"]) if row else Decimal("0.00")

    if Decimal(monto) > ahorro_total:
        st.error(f"❌ La socia no tiene suficiente ahorro. Disponible: ${ahorro_total}.")
        return

    # ============================================================
    # Validación — caja suficiente
    # ============================================================
    id_caja = obtener_o_crear_reunion(fecha_prestamo)
    cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    saldo_caja = Decimal(cursor.fetchone()["saldo_final"])

    if Decimal(monto) > saldo_caja:
        st.error(f"❌ Saldo insuficiente en caja. Disponible: ${saldo_caja}.")
        return

    # ============================================================
    # Cálculo de intereses
    # ============================================================
    interes_total = Decimal(monto) * (Decimal(tasa) / 100)
    total_pagar = Decimal(monto) + interes_total

    # ============================================================
    # Registrar préstamo
    # ============================================================
    cursor.execute("""
        INSERT INTO Prestamo(
            `Fecha del préstamo`, `Monto prestado`, `Interes_total`,
            `Tasa de interes`, `Plazo`, `Cuotas`, `Saldo pendiente`,
            Estado_del_prestamo, Id_Grupo, Id_Socia, Id_Caja
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,'activo',1,%s,%s)
    """, (
        fecha_prestamo, monto, float(interes_total),
        tasa, plazo, cuotas, float(total_pagar),
        id_socia, id_caja
    ))
    id_prestamo_generado = cursor.lastrowid

    # ============================================================
    # Descontar ahorro
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
    # Restar de caja
    # ============================================================
    registrar_movimiento(
        id_caja=id_caja,
        tipo="Egreso",
        categoria=f"Préstamo otorgado – {socia_sel}",
        monto=float(monto)
    )

    # ============================================================
    # Generar cuotas (cada 15 días)
    # ============================================================
    valor_cuota = total_pagar / Decimal(cuotas)
    fecha_base = datetime.strptime(fecha_prestamo, "%Y-%m-%d")

    lista_cuotas = []

    for n in range(1, cuotas + 1):
        fecha_cuota = fecha_base + timedelta(days=15 * n)
        fecha_str = fecha_cuota.strftime("%Y-%m-%d")

        cursor.execute("""
            INSERT INTO Cuotas_prestamo
            (Id_Prestamo, Numero_cuota, Fecha_programada, Monto_cuota, Estado)
            VALUES (%s,%s,%s,%s,'pendiente')
        """, (
            id_prestamo_generado, n,
            fecha_str,
            round(float(valor_cuota), 2)
        ))

        lista_cuotas.append((n, fecha_str, round(float(valor_cuota), 2)))

    con.commit()

    # ============================================================
    # RESUMEN FINAL
    # ============================================================
    st.success("✔ Préstamo autorizado correctamente.")

    st.markdown("## 📘 Resumen del préstamo aprobado")
    st.write(f"**📅 Fecha:** {fecha_prestamo}")
    st.write(f"**👩 Socia:** {socia_sel}")
    st.write(f"**💵 Monto prestado:** ${monto}")
    st.write(f"**📈 Interés aplicado ({tasa}%):** ${round(float(interes_total), 2)}")
    st.write(f"**💰 Total a pagar:** ${round(float(total_pagar), 2)}")
    st.write(f"**🗓 Número de cuotas:** {cuotas}")

    st.markdown("### 📑 Calendario de cuotas (cada 15 días)")
    for n, f, val in lista_cuotas:
        st.write(f"• **Cuota {n}:** {f} — ${val}")
