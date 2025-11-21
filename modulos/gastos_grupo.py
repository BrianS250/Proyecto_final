import streamlit as st
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha
from datetime import date


def gastos_grupo():

    st.header("💸 Registrar gastos del grupo")

    con = obtener_conexion()
    cursor = con.cursor()

    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    descripcion = st.text_input("Descripción del gasto")
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # Obtener saldo disponible de la caja
    try:
        saldo_actual = obtener_saldo_por_fecha(fecha)
        st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo_actual:.2f}**")
    except:
        saldo_actual = 0
        st.error("No se pudo obtener el saldo de caja.")

    if st.button("💾 Registrar gasto"):

        # VALIDACIÓN PRINCIPAL:
        if monto > saldo_actual:
            st.error(f"❌ El gasto supera el saldo disponible. Saldo: ${saldo_actual:.2f} — Gasto: ${monto:.2f}")
            return

        # Si pasa la validación → registrar
        cursor.execute("""
            INSERT INTO GastosGrupo(Descripcion, Monto, Fecha)
            VALUES(%s, %s, %s)
        """, (descripcion, monto, fecha))
        con.commit()

        # Registrar movimiento EN CAJA (egreso)
        id_caja = obtener_o_crear_reunion(fecha)
        registrar_movimiento(id_caja, "Egreso", f"Gasto – {descripcion}", monto)

        st.success("Gasto registrado correctamente y descontado de caja.")
        st.rerun()

    cursor.close()
    con.close()
