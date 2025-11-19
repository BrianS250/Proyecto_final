import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion


def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # ======================================================
    # OBTENER SOCIAS
    # ======================================================
    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    lista_socias = {nombre: ids for (ids, nombre) in socias}

    # ======================================================
    # FORMULARIO
    # ======================================================
    with st.form("form_prestamo"):

        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today())

        nombre_socia = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[nombre_socia]

        proposito = st.text_input("🎯 Propósito del préstamo (opcional)")

        monto = st.number_input("💵 Monto solicitado", min_value=1, step=1)

        tasa_interes = st.number_input("📈 Tasa de interés (%)", min_value=1, value=10)

        plazo = st.number_input("🗓 Plazo (meses)", min_value=1)
        cuotas = st.number_input("📑 Número de cuotas", min_value=1, value=plazo)

        firma = st.text_input("✍️ Firma del directivo que autoriza")

        enviar = st.form_submit_button("✅ Autorizar préstamo")

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================
    if enviar:

        # 1. Verificar caja
        cursor.execute("SELECT Id_Caja, Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        caja = cursor.fetchone()

        if not caja:
            st.error("❌ No existe caja activa.")
            return

        id_caja, saldo_actual = caja

        if monto > saldo_actual:
            st.error(f"❌ Fondos insuficientes. Saldo disponible: ${saldo_actual}")
            return

        saldo_pendiente = monto

        try:
            # --------------------------------------------------
            # 2. INSERTAR PRÉSTAMO
            # --------------------------------------------------
            cursor.execute(f"""
                INSERT INTO Prestamo(
                    `Fecha del préstamo`,
                    `Monto prestado`,
                    `Tasa de interes`,
                    `Plazo`,
                    `Cuotas`,
                    `Saldo pendiente`,
                    `Estado del préstamo`,
                    Id_Grupo,
                    Id_Socia,
                    Id_Caja
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha_prestamo,
                monto,
                tasa_interes,
                plazo,
                cuotas,
                saldo_pendiente,
                "activo",
                1,
                id_socia,
                id_caja
            ))

            # --------------------------------------------------
            # 3. REGISTRAR EGRESO EN CAJA
            # --------------------------------------------------
            cursor.execute("""
                INSERT INTO Caja(Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento)
                VALUES (%s,%s,%s,%s,%s)
            """,
            (
                f"Préstamo otorgado a: {nombre_socia}",
                -monto,
                saldo_actual - monto,
                1,
                3
            ))

            con.commit()

            st.success("✅ Préstamo autorizado correctamente.")
            st.info(f"Nuevo saldo en caja: ${saldo_actual - monto}")

            # ======================================================
            # 📌 RESUMEN DETALLADO DEL PRÉSTAMO
            # ======================================================
            tasa_decimal = tasa_interes / 100
            total_interes = monto * tasa_decimal
            total_pagar = monto + total_interes
            pago_por_cuota = total_pagar / cuotas

            st.markdown("---")
            st.subheader("📘 Resumen del préstamo")

            st.write(f"""
            **📅 Fecha del préstamo:** {fecha_prestamo}  
            **👩 Id de la socia:** {id_socia}  
            **👩 Nombre:** {nombre_socia}  

            **💵 Monto prestado:** ${monto:,.2f}  
            **📈 Tasa de interés:** {tasa_interes}%  
            **💰 Interés total generado:** ${total_interes:,.2f}  

            **🧮 Total a pagar:** ${total_pagar:,.2f}  
            **📑 Número de cuotas:** {cuotas}  
            **💸 Pago por cuota:** ${pago_por_cuota:,.2f}  
            """)

            st.success("✔ Cálculo realizado correctamente.")

        except Exception as e:
            con.rollback()
            st.error(f"❌ Error al registrar el préstamo: {e}")
