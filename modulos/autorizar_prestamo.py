import streamlit as st
from datetime import date, datetime, timedelta
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento
from modulos.reglas_utils import obtener_reglas


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    # ============================================================
    # 🔗 Cargar reglas
    # ============================================================
    reglas = obtener_reglas()
    if not reglas:
        st.error("⚠ No existen reglas internas registradas.")
        return

    prestamo_maximo = float(reglas["prestamo_maximo"])
    interes_por_10 = float(reglas["interes_por_10"])
    plazo_maximo = int(reglas["plazo_maximo"])

    # ============================================================
    # Cargar socias
    # ============================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    lista_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    # ============================================================
    # FORMULARIO
    # ============================================================

    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today()).strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia", list(lista_socias.keys()))
        id_socia = lista_socias[socia_sel]

        # ============================================================
        # 🔒 MONTO — BLOQUEO TOTAL DE LETRAS
        # ============================================================
        monto_raw = st.text_input(
            "💵 Monto prestado ($):",
            value="",
            placeholder=f"Máximo permitido: ${prestamo_maximo}"
        )

        # Limpieza automática
        limpio = "".join([c for c in monto_raw if c.isdigit() or c == "."])

        # Solo un punto
        if limpio.count(".") > 1:
            partes = limpio.split(".")
            limpio = partes[0] + "." + "".join(partes[1:])

        # Máximo 2 decimales
        if "." in limpio:
            ent, dec = limpio.split(".", 1)
            dec = dec[:2]
            limpio = ent + "." + dec

        # Convertir
        try:
            monto = float(limpio) if limpio else 0.0
        except:
            monto = 0.0

        if monto_raw != limpio:
            st.warning("🔎 Se removieron caracteres no válidos.")

        # ============================================================
        # Interés automático según reglas
        # ============================================================
        interes_sugerido = round((monto / 10) * interes_por_10, 2)

        st.text_input("📈 Interés (%) (automático)", value=str(interes_sugerido), disabled=True)

        plazo = st.number_input("🗓 Plazo (semanas):", min_value=1, max_value=plazo_maximo)
        cuotas = st.number_input("📑 Número de cuotas:", min_value=1)
        firma = st.text_input("✍️ Firma directiva")

        enviar = st.form_submit_button("Autorizar préstamo")

    if not enviar:
        return

    # ============================================================
    # VALIDACIONES
    # ============================================================

    if monto <= 0:
        st.error("❌ Ingrese un monto válido.")
        return

    if monto > prestamo_maximo:
        st.error(f"❌ El monto máximo permitido es: ${prestamo_maximo}.")
        return

    # Ahorro disponible
    cursor.execute("""
        SELECT `Saldo acumulado` 
        FROM Ahorro 
        WHERE Id_Socia=%s 
        ORDER BY Id_Ahorro DESC LIMIT 1
    """, (id_socia,))
    row = cursor.fetchone()
    ahorro_total = Decimal(row["Saldo acumulado"]) if row else Decimal("0")

    if Decimal(monto) > ahorro_total:
        st.error(f"❌ La socia solo tiene ${ahorro_total} de ahorro.")
        return

    # Caja suficiente
    id_caja = obtener_o_crear_reunion(fecha_prestamo)
    cursor.execute("SELECT saldo_final FROM caja_reunion WHERE id_caja=%s", (id_caja,))
    saldo_caja = Decimal(cursor.fetchone()["saldo_final"])

    if Decimal(monto) > saldo_caja:
        st.error(f"❌ Caja insuficiente. Disponible: ${saldo_caja}.")
        return

    # ============================================================
    # Cálculos finales
    # ============================================================
    interes_total = Decimal(interes_sugerido)
    total_pagar = Decimal(monto) + interes_total
    valor_cuota = round(float(total_pagar / cuotas), 2)

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
        fecha_prestamo, monto, interes_total,
        interes_por_10, plazo, cuotas, total_pagar,
        id_socia, id_caja
    ))

    id_prestamo = cursor.lastrowid

    # ============================================================
    # Registrar cuotas
    # ============================================================
    fecha_base = datetime.strptime(fecha_prestamo, "%Y-%m-%d")

    for n in range(1, cuotas + 1):
        fecha_cuota = fecha_base + timedelta(days=15 * n)
        cursor.execute("""
            INSERT INTO Cuotas_prestamo
            (Id_Prestamo, Numero_cuota, Fecha_programada, Monto_cuota, Estado)
            VALUES (%s,%s,%s,%s,'pendiente')
        """, (
            id_prestamo, n,
            fecha_cuota.strftime("%Y-%m-%d"),
            valor_cuota
        ))

    # Descontar ahorro
    nuevo_ahorro = ahorro_total - Decimal(monto)
    cursor.execute("""
        INSERT INTO Ahorro(
            `Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
            `Comprobante digital`, `Saldo acumulado`, Id_Socia
        )
        VALUES (%s,%s,'Descuento préstamo','---',%s,%s)
    """, (fecha_prestamo, -Decimal(monto), nuevo_ahorro, id_socia))

    # Registrar movimiento de caja
    registrar_movimiento(
        id_caja=id_caja,
        tipo="Egreso",
        categoria=f"Préstamo otorgado – {socia_sel}",
        monto=float(monto)
    )

    con.commit()

    # ============================================================
    # RESUMEN FINAL
    # ============================================================

    st.success("✔ Préstamo autorizado correctamente.")
    st.subheader("📄 Resumen del préstamo")

    st.write(f"**Fecha:** {fecha_prestamo}")
    st.write(f"**Socia:** {socia_sel}")
    st.write(f"**Monto prestado:** ${monto}")
    st.write(f"**Interés total:** ${interes_total}")
    st.write(f"**Total a pagar:** ${total_pagar}")
    st.write(f"**Número de cuotas:** {cuotas}")
    st.write("### Calendario de cuotas:")

    for n in range(1, cuotas + 1):
        fecha_cuota = fecha_base + timedelta(days=15 * n)
        st.write(f"📌 **Cuota {n}:** {fecha_cuota.strftime('%Y-%m-%d')} — ${valor_cuota}")

