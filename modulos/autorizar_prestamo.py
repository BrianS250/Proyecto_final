import streamlit as st
from modulos.conexion import obtener_conexion
from datetime import date, timedelta

def autorizar_prestamo():

    st.title("💳 Autorizar préstamo")
    st.write("Complete la información para autorizar un nuevo préstamo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # Obtener socias del grupo (Id_Usuario)
    cursor.execute("""
        SELECT Id_Usuario, Nombre
        FROM Empleado
        WHERE Id_Rol = 3   -- Rol socia
    """)
    socias = cursor.fetchall()

    lista_socias = {nombre: idu for (idu, nombre) in socias}

    # FORMULARIO
    with st.form("form_prestamo"):
        fecha_prestamo = st.date_input("📅 Fecha del préstamo", date.today())

        socia_nombre = st.selectbox("👩 Socia que recibe el préstamo", list(lista_socias.keys()))
        id_socia = lista_socias[socia_nombre]

        proposito = st.text_input("🎯 Propósito del préstamo")

        monto = st.number_input("💵 Monto solicitado", min_value=1, step=1)

        tasa_interes = st.number_input("📈 Tasa de interés (%)", min_value=1, value=10)

        plazo = st.number_input("🗓 Plazo (meses)", min_value=1, step=1)

        cuotas = st.number_input("📑 Número de cuotas", min_value=1, value=plazo)

        firma = st.text_input("✍️ Firma digital")

        enviado = st.form_submit_button("✅ Autorizar préstamo")

    if enviado:

        # 1. Verificar disponibilidad de caja
        cursor.execute("SELECT Id_Caja, Saldo_actual FROM Caja ORDER BY Id_Caja DESC LIMIT 1")
        caja = cursor.fetchone()

        if caja is None:
            st.error("❌ No existe caja activa.")
            return

        id_caja, saldo_actual = caja

        if monto > saldo_actual:
            st.error(f"❌ No hay suficiente dinero en caja. Saldo disponible: ${saldo_actual}")
            return

        # 2. Calcular saldo pendiente
        saldo_pendiente = monto

        # 3. INSERT en tabla Prestamo
        try:
            cursor.execute("""
                INSERT INTO Prestamo(
                    Fecha_del_prestamo, Monto_prestado, Tasa_de_interes, 
                    Plazo, Cuotas, Saldo_pendiente, Estado_del_prestamo, 
                    Id_Grupo, Id_Usuario, Id_Caja
                )
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                fecha_prestamo,
                monto,
                tasa_interes,
                plazo,
                cuotas,
                saldo_pendiente,
                "activo",
                1,  # Id_Grupo por defecto (ajústalo si manejas varios grupos)
                id_socia,
                id_caja
            ))

            # 4. Registrar movimiento en caja
            cursor.execute("""
                INSERT INTO Caja(Concepto, Monto, Saldo_actual, Id_Grupo, Id_Tipo_movimiento)
                VALUES (%s,%s,%s,%s,%s)
            """,
            (
                "Desembolso préstamo",
                -monto,
                saldo_actual - monto,
                1,  # Grupo
                2   # Tipo movimiento: egreso
            ))

            con.commit()

            st.success("✅ Préstamo autorizado exitosamente.")
            st.info(f"Saldo restante en caja: ${saldo_actual - monto}")

        except Exception as e:
            st.error(f"❌ Error al autorizar préstamo: {e}")
            con.rollback()
