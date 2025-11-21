import streamlit as st
from datetime import date
from modulos.conexion import obtener_conexion

# Caja por reunión (ya existente)
from modulos.caja import obtener_o_crear_reunion, registrar_movimiento


def gastos_grupo():

    st.header("🧾 Registro de otros gastos del grupo")

    # ---------------------------------------------
    # FECHA DEL GASTO
    # ---------------------------------------------
    fecha_raw = st.date_input("📅 Fecha del gasto", date.today())
    fecha_gasto = fecha_raw.strftime("%Y-%m-%d")

    # ---------------------------------------------
    # DATOS DEL GASTO
    # ---------------------------------------------
    concepto = st.text_input("📝 Concepto del gasto (ej. 'Refrigerio', 'Materiales')")
    responsable = st.text_input("👤 Responsable del gasto (opcional)")
    monto = st.number_input("💵 Monto del gasto ($)", min_value=0.25, step=0.25)

    if st.button("➖ Registrar gasto"):

        if concepto.strip() == "":
            st.warning("⚠ Debe escribir un concepto del gasto.")
            return

        try:
            # 1️⃣ Crear u obtener la reunión según la fecha
            id_caja = obtener_o_crear_reunion(fecha_gasto)

            # 2️⃣ Registrar el movimiento en caja (EGRESO)
            descripcion = f"Gasto del grupo – {concepto}"
            if responsable.strip() != "":
                descripcion += f" (Responsable: {responsable})"

            registrar_movimiento(
                id_caja,
                "Egreso",
                descripcion,
                monto
            )

            st.success("✔ Gasto registrado y descontado de la caja del día.")

            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar gasto: {e}")
