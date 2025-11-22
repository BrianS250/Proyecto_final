import streamlit as st
import pandas as pd
from datetime import date, timedelta
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


# ============================================================
# AUTORIZAR PRÉSTAMO – SISTEMA CVX
# ============================================================
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

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    opciones_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s['Id_Socia'] for s in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo_raw = st.date_input("📅 Fecha del préstamo", date.today())
        fecha_prestamo = fecha_prestamo_raw.strftime("%Y-%m-%d")

        socia_sel = st.selectbox("👩 Socia que recibe el préstamo", list(opciones_socias.keys()))
        id_socia = opciones_socias[socia_sel]

        monto = st.number_input("💵 Monto prestado ($):", min_value=1, max_value=300, step=1)
        tasa = st.number_input("📈 Tasa mensual (%)", min_value=1, max_value=20, value=10)
        plazo_meses = st.number_input("🗓 Plazo (meses, máximo 4):", min_value=1, max_value=4)
        cuotas = st.number_input("📑 Número de cuotas (quincenales)", min_value=2, max_value=8, value=plazo_meses * 2)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    if not enviar:
        return

    # ======================================================
    # VALIDACIONES
    # ======================================================

    # AHORRO
    cursor.execute("""
        SELECT `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia=%s
        ORDER BY Id_Ahorro DESC LIMIT 1
    """, (id_socia,))
    row = cursor.fetchone()
    ahorro = row["Saldo acumulado"] if row else 0

    if monto > ahorro:
        st.error(f"""
        ❌ Ahorro insuficiente.
        Ahorro: ${ahorro:.2f}
        Solicitado: ${monto:.2f}
        """)
        return

    # PRÉSTAMO ACTIVO
    cursor.execute("""
        SELECT Id_Préstamo FROM Prestamo
        WHERE Id_Socia=%s AND Estado_del_prestamo='activo'
    """, (id_socia,))
    if cursor.fetchone():
        st.error("❌ La socia ya tiene un préstamo activo.")
        return

    # CAJA
    cursor.execute("SELECT saldo_final FROM caja_reunion ORDER BY fecha DESC LIMIT 1")
    row = cursor.fetchone()
    saldo_caja = row["saldo_final"] if row else 0

    if monto > saldo_caja:
        st.error(f"❌ Fondos insuficientes en caja. Disponible: ${saldo_caja}")
        return

    # ======================================================
    # CÁLCULOS FINANCIEROS
    # ======================================================
    tasa_mensual = tasa / 100
    interes_total = round(monto * tasa_mensual * plazo_meses, 2)
    total_a_pagar = round(monto + interes_total, 2)

    cuota_fija = round(total_a_pagar / cuotas, 2)
    interes_por_cuota = round(interes_total / cuotas, 2)

    # GENERAR FECHAS
    fechas_cuotas = []
    for i in range(cuotas):
        fecha_cuota = fecha_prestamo_raw + timedelta(days=15 * (i + 1))
        fechas_cuotas.append(fecha_cuota.strftime("%Y-%m-%d"))

    # ======================================================
    # GUARDAR PRÉSTAMO EN BD
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
            `Estado_del_prestamo`,
            Id_Grupo,
            Id_Socia
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,'activo',1,%s)
    """, (fecha_prestamo, monto, interes_total, tasa, plazo_meses, cuotas, total_a_pagar, id_socia))

    con.commit()

    # ======================================================
    # REGISTRAR EGRESO EN CAJA
    # ======================================================
    id_caja = obtener_o_crear_reunion(fecha_prestamo)

    registrar_movimiento(
        id_caja,
        "Egreso",
        f"Préstamo otorgado a {socia_sel}",
        float(monto)
    )

    # ======================================================
    # RESUMEN PROFESIONAL
    # ======================================================
    st.success("✔ Préstamo autorizado correctamente.")
    st.subheader("📄 Resumen del préstamo")

    resumen = {
        "Socia": socia_sel,
        "Monto prestado": f"${monto:.2f}",
        "Tasa mensual": f"{tasa}%",
        "Interés total": f"${interes_total:.2f}",
        "Total a pagar": f"${total_a_pagar:.2f}",
        "Plazo": f"{plazo_meses} meses",
        "Cuotas quincenales": cuotas,
        "Cuota fija": f"${cuota_fija:.2f}",
        "Interés por cuota": f"${interes_por_cuota:.2f}",
        "Saldo pendiente inicial": f"${total_a_pagar:.2f}"
    }

    st.table(pd.DataFrame(resumen.items(), columns=["Detalle", "Valor"]))

    st.subheader("📅 Calendario de pagos")
    df_cal = pd.DataFrame({
        "Cuota": list(range(1, cuotas + 1)),
        "Fecha": fechas_cuotas,
        "Monto": [cuota_fija] * cuotas,
        "Interés": [interes_por_cuota] * cuotas,
        "Capital": [round(cuota_fija - interes_por_cuota, 2)] * cuotas
    })
    st.dataframe(df_cal, hide_index=True)

    cursor.close()
    con.close()
