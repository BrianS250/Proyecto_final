import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

# NUEVA CAJA POR REUNIÓN
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def ahorro():

    st.header("💰 Registro de Ahorros")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------------------------
    # 1️⃣ SOCIAS
    # ---------------------------------------------------------
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia ORDER BY Id_Socia ASC")
    socias = cursor.fetchall()

    dict_socias = {f"{id_socia} - {nombre}": id_socia for id_socia, nombre in socias}

    socia_sel = st.selectbox("👩 Seleccione la socia:", dict_socias.keys())
    id_socia = dict_socias[socia_sel]

    # ---------------------------------------------------------
    # 2️⃣ HISTORIAL DE APORTES
    # ---------------------------------------------------------
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
        for ap in aportes:
            st.write(f"""
                **ID:** {ap[0]}  
                **Fecha:** {ap[1]}  
                **Monto:** ${ap[2]}  
                **Tipo:** {ap[3]}  
                **Comprobante:** {ap[4]}  
                **Saldo acumulado:** ${ap[5]}  
            """)
    else:
        st.info("Esta socia aún no tiene aportes registrados.")

    # ---------------------------------------------------------
    # 3️⃣ NUEVO APORTE
    # ---------------------------------------------------------
    st.markdown("---")
    st.header("🧾 Registrar nuevo aporte")

    fecha_aporte_raw = st.date_input("📅 Fecha del aporte", value=date.today())
    fecha_aporte = fecha_aporte_raw.strftime("%Y-%m-%d")

    monto = st.number_input("💵 Monto del aporte ($)", min_value=1.00, step=1.00)
    tipo = st.selectbox("📌 Tipo de aporte", ["Ordinario", "Extraordinario"])
    comprobante = st.text_input("📎 Comprobante digital")

    if st.button("💾 Registrar aporte"):

        try:
            # ---------------------------------------------------------
            # 4️⃣ OBTENER SALDO ANTERIOR
            # ---------------------------------------------------------
            cursor.execute("""
                SELECT `Saldo acumulado`
                FROM Ahorro
                WHERE Id_Socia = %s
                ORDER BY Id_Ahorro DESC
                LIMIT 1
            """, (id_socia,))
            
            row = cursor.fetchone()
            saldo_anterior = row[0] if row else 0

            nuevo_saldo = saldo_anterior + monto

            # ---------------------------------------------------------
            # 5️⃣ INSERTAR EN TABLA AHORRO
            # ---------------------------------------------------------
            cursor.execute("""
                INSERT INTO Ahorro
                (`Fecha del aporte`, `Monto del aporte`, `Tipo de aporte`,
                 `Comprobante digital`, `Saldo acumulado`, Id_Socia)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                fecha_aporte,
                monto,
                tipo,
                comprobante,
                nuevo_saldo,
                id_socia
            ))

            # ---------------------------------------------------------
            # 6️⃣ INSERTAR EN CAJA POR REUNIÓN (INGRESO)
            # ---------------------------------------------------------
            id_caja = obtener_o_crear_reunion(fecha_aporte)
            registrar_movimiento(
                id_caja,
                "Ingreso",
                f"Ahorro – Socia {id_socia}",
                monto
            )

            con.commit()
            st.success("Aporte registrado y agregado a caja por reunión.")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar aporte: {e}")
