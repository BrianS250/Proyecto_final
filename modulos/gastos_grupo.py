import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento, obtener_saldo_por_fecha


# ============================================================
# REGISTRAR GASTOS DEL GRUPO
# ============================================================
def gastos_grupo():

    st.title("💸 Registrar gastos del grupo")

    # Fecha del gasto
    fecha_raw = st.date_input("Fecha del gasto", date.today())
    fecha = fecha_raw.strftime("%Y-%m-%d")

    # Nombre de la persona responsable
    responsable = st.text_input("👤 Nombre de la persona responsable del gasto")

    # DUI (solo números, 9 dígitos)
    dui_input = st.text_input("DUI (9 dígitos)", max_chars=9)

    # Validación: DUI solo números
    if dui_input and not dui_input.isdigit():
        st.error("⚠️ El DUI solo debe contener números (9 dígitos).")

    # DUI formateado automáticamente
    dui_formateado = ""
    if len(dui_input) == 9:
        dui_formateado = f"{dui_input[:8]}-{dui_input[8]}"

    # Descripción del gasto
    descripcion = st.text_input("Descripción del gasto")

    # Monto
    monto = st.number_input("Monto del gasto ($)", min_value=0.25, step=0.25)

    # Mostrar saldo disponible en caja
    try:
        saldo = obtener_saldo_por_fecha(fecha)
        st.info(f"💰 Saldo disponible en caja para {fecha}: **${saldo:.2f}**")
    except:
        st.warning("⚠ No se pudo obtener el saldo de caja.")
        saldo = 0

    # ============================================================
    # BOTÓN PARA REGISTRAR EL GASTO
    # ============================================================
    if st.button("💾 Registrar gasto"):

        # Validaciones generales
        if responsable.strip() == "":
            st.warning("⚠ Debe ingresar el nombre de la persona responsable.")
            return

        if dui_input.strip() == "" or len(dui_input) != 9:
            st.warning("⚠ El DUI debe tener exactamente 9 dígitos.")
            return

        if descripcion.strip() == "":
            st.warning("⚠ Debe ingresar una descripción del gasto.")
            return

        # Validación de fondos suficientes
        if monto > saldo:
            st.error(f"❌ No se puede registrar el gasto. El monto (${monto:.2f}) "
                     f"es mayor que el saldo disponible en caja (${saldo:.2f}).")
            return

        # ===========================================
        # GUARDAR GASTO EN BD
        # ===========================================
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            INSERT INTO Gastos_grupo(Fecha_gasto, Descripcion, Monto, Responsable, DUI)
            VALUES(%s, %s, %s, %s, %s)
        """, (fecha, descripcion, monto, responsable, dui_formateado))

        con.commit()

        # ===========================================
        # RESTAR AUTOMÁTICAMENTE DE CAJA
        # ===========================================
        id_caja = obtener_o_crear_reunion(fecha)

        registrar_movimiento(
            id_caja,
            "Egreso",
            f"Gasto – {descripcion} (Responsable: {responsable}, DUI: {dui_formateado})",
            monto
        )

        st.success("✅ Gasto registrado y descontado de la caja correctamente.")
        st.rerun()
