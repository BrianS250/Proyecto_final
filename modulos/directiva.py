import streamlit as st

# --------------------------------------------------
# 🧩 INTERFAZ DE DIRECTIVA DEL GRUPO
# --------------------------------------------------
def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    # Menú lateral de opciones
    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        [
            "📅 Registrar reunión y asistencia",
            "💰 Registrar préstamos o pagos",
            "⚠️ Aplicar multas",
            "📊 Generar actas y reportes"
        ]
    )

    # --------------------------------------------------
    # OPCIÓN 1 — Reuniones y asistencias
    # --------------------------------------------------
    if opcion == "📅 Registrar reunión y asistencia":
        st.subheader("📅 Registro de reunión")
        fecha = st.date_input("Fecha de la reunión")
        tema = st.text_input("Tema principal")
        asistentes = st.text_area("Lista de asistentes (separados por comas)")
        if st.button("Guardar reunión"):
            st.success("✅ Reunión registrada correctamente")

    # --------------------------------------------------
    # OPCIÓN 2 — Préstamos y pagos
    # --------------------------------------------------
    elif opcion == "💰 Registrar préstamos o pagos":
        st.subheader("💰 Registro de préstamos o pagos")
        tipo = st.selectbox("Tipo de registro", ["Préstamo", "Pago"])
        monto = st.number_input("Monto ($)", min_value=0.01, step=0.01)
        descripcion = st.text_area("Descripción")
        if st.button("Guardar movimiento"):
            st.success(f"✅ {tipo} registrado correctamente por ${monto:.2f}")

    # --------------------------------------------------
    # OPCIÓN 3 — Multas
    # --------------------------------------------------
    elif opcion == "⚠️ Aplicar multas":
        st.subheader("⚠️ Aplicación de multas")
        miembro = st.text_input("Nombre del miembro sancionado")
        motivo = st.text_area("Motivo de la multa")
        monto_multa = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)
        if st.button("Registrar multa"):
            st.success(f"✅ Multa aplicada a {miembro} por ${monto_multa:.2f}")

    # --------------------------------------------------
    # OPCIÓN 4 — Reportes
    # --------------------------------------------------
    elif opcion == "📊 Generar actas y reportes":
        st.subheader("📊 Reportes del grupo")
        st.info("Genera actas de reuniones, listados de aportes y balances financieros.")
        if st.button("Descargar reporte general"):
            st.success("📁 Reporte generado y listo para descargar.")
