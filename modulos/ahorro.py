import streamlit as st 
from datetime import date
from decimal import Decimal

from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento
from modulos.reglas_utils import obtener_reglas



# ============================================================
# FUNCIÓN PRINCIPAL — REGISTRO DE AHORRO
# ============================================================
def ahorro():

    st.header("💰 Registro de Ahorros")

    # ============================================================
    # 1️⃣ LEER REGLAS INTERNAS (ahorro mínimo)
    # ============================================================
    reglas = obtener_reglas()

    if not reglas:
        st.error("⚠ No existen reglas internas registradas. Regístrelas primero.")
        return

    ahorro_minimo = float(reglas.get("ahorro_minimo", 0))

    # ============================================================
    # 2️⃣ SOCIAS
    # ============================================================
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dict_socias = {f"{s['Id_Socia']} - {s['Nombre']}": s["Id_Socia"] for s in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ============================================================
    # 3️⃣ HISTORIAL DE APORTES
    # ============================================================
    cursor.execute("""
        SELECT 
            Id_Ahorro,
            `Fecha del aporte`,
            `Monto del aporte`,
            `Tipo de aporte`,
            `Comprobante digital`,
            `Saldo acumulado`
        FROM Ahorro
        WHERE Id_Socia = %s
        ORDER BY Id_Ahorro DESC
    """, (id_socia,))
    aportes = cursor.fetchall()

    st.subheader("📄 Historial de aportes")

    if aportes:
        import pandas as pd

        df = pd.DataFrame(aportes)
        st.dataframe(df, use_container_width=True)

        ultimo_saldo = aportes[0]["Saldo acumulado"]
        st.success(f"💵 **Saldo actual acumulado:** ${ultimo_saldo}")
    else:
        st.info("Esta socia aún no tiene aportes registrados.")
        ultimo_saldo = 0

    # ============================================================
    # 4️⃣ NUEVO APORTE
    # ============================================================
    st.markdown("---")
    st.header("🧾 Registrar nuevo aporte")

    fecha_aporte_raw = st.date_input("📅 Fecha del aporte", value=date.today())
    fecha_aporte = fecha_aporte_raw.strftime("%Y-%m-%d")

    # ------------------------------------------------------------
    # Tipo de aporte
    # ------------------------------------------------------------
    tipo = st.selectbox("📌 Tipo de aporte", ["Ordinario", "Extraordinario"])

    if tipo == "Ordinario":
        st.info(f"🔒 Aporte ordinario mínimo según reglamento: **${ahorro_minimo}**")
        monto = st.number_input(
            "💵 Monto del aporte ($)",
            min_value=ahorro_minimo,
            value=ahorro_minimo,
            step=0.25
        )
    else:
        monto = st.number_input(
            "💵 Monto del aporte ($)",
            min_value=0.25,
            value=1.00,
            step=0.25
        )
        st.caption("Los aportes extraordinarios no tienen un mínimo definido.")

    comprobante = st.text_input("📎 Comprobante digital (opcional)")

    # ============================================================
    # BOTÓN PARA REGISTRAR
    # ============================================================
    if st.button("💾 Registrar aporte"):

        try:
            # ------------------------------------------
            # Sumar al saldo anterior
            # ------------------------------------------
            saldo_anterior = Decimal(str(ultimo_saldo))
            monto_decimal = Decimal(str(monto))

            if monto_decimal <= 0:
                st.error("❌ El monto debe ser mayor que 0.")
                return

            nuevo_saldo = saldo_anterior + monto_decimal

            # ------------------------------------------
            # Registrar aporte
            # ------------------------------------------
            cursor.execute("""
                INSERT INTO Ahorro
                (`Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
                 `Comprobante digital`, `Saldo acumulado`, Id_Socia)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                fecha_aporte,
                monto_decimal,
                tipo,
                comprobante if comprobante else "---",
                nuevo_saldo,
                id_socia
            ))

            # ------------------------------------------
            # Caja única → registrar ingreso
            # ------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_aporte)

            registrar_movimiento(
                id_caja=id_caja,
                tipo="Ingreso",
                categoria=f"Ahorro – {socia_sel}",
                monto=float(monto_decimal)
            )

            con.commit()
            st.success("✔ Aporte registrado correctamente.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar aporte: {e}")

