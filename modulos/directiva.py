import streamlit as st
from datetime import datetime

# ----------------------------------------
# 🎯 INTERFAZ DE LA DIRECTIVA DEL GRUPO
# ----------------------------------------

def interfaz_directiva():
    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Administra las reuniones, aportes y préstamos de tu grupo.")

    # --- Menú lateral ---
    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        [
            "📅 Registrar reunión y asistencia",
            "💰 Registrar aportes o pagos",
            "🏦 Registrar préstamo o abono",
            "⚠️ Aplicar multa",
            "📜 Generar acta o reporte"
        ]
    )

    # --- Sección 1: Reuniones y Asistencias ---
    if opcion == "📅 Registrar reunión y asistencia":
        st.subheader("📅 Registro de reuniones y asistencia")
        fecha = st.date_input("Fecha de la reunión", datetime.today())
        tema = st.text_input("Tema de la reunión")
        asistentes = st.text_area("Asistentes (separa con comas)")
        acuerdos = st.text_area("Acuerdos tomados")

        if st.button("✅ Guardar reunión"):
            st.success(f"Reunión registrada para el {fecha}.")
            st.info("Tema: " + tema)
            st.write("Asistentes:", asistentes)
            st.write("Acuerdos:", acuerdos)

    # --- Sección 2: Aportes ---
    elif opcion == "💰 Registrar aportes o pagos":
        st.subheader("💰 Registro de aportes")
        miembro = st.text_input("Nombre del miembro")
        monto = st.number_input("Monto del aporte ($)", min_value=0.01, step=0.01)
        fecha = st.date_input("Fecha del pago", datetime.today())

        if st.button("💾 Guardar aporte"):
            st.success(f"Aporte de ${monto:.2f} registrado para {miembro} el {fecha}.")

    # --- Sección 3: Préstamos ---
    elif opcion == "🏦 Registrar préstamo o abono":
        st.subheader("🏦 Registro de préstamos")
        miembro = st.text_input("Nombre del solicitante")
        monto = st.number_input("Monto del préstamo ($)", min_value=1.0, step=1.0)
        fecha = st.date_input("Fecha del préstamo", datetime.today())
        tipo = st.selectbox("Tipo de registro", ["Nuevo préstamo", "Abono a préstamo"])

        if st.button("💾 Guardar registro"):
            if tipo == "Nuevo préstamo":
                st.success(f"Préstamo de ${monto:.2f} otorgado a {miembro} el {fecha}.")
            else:
                st.success(f"Abono de ${monto:.2f} registrado para {miembro} el {fecha}.")

    # --- Sección 4: Multas ---
    elif opcion == "⚠️ Aplicar multa":
        st.subheader("⚠️ Registro de multas por mora o inasistencia")
        miembro = st.text_input("Nombre del miembro multado")
        razon = st.selectbox("Motivo de la multa", ["Inasistencia", "Mora en pago", "Otro"])
        monto = st.number_input("Monto de la multa ($)", min_value=0.5, step=0.5)
        fecha = st.date_input("Fecha de la multa", datetime.today())

        if st.button("💾 Registrar multa"):
            st.error(f"Multa de ${monto:.2f} aplicada a {miembro} por {razon} el {fecha}.")

    # --- Sección 5: Reportes ---
    elif opcion == "📜 Generar acta o reporte":
        st.subheader("📜 Generación de actas y reportes")
        tipo = st.selectbox("Selecciona tipo de documento", ["Acta de reunión", "Reporte de aportes", "Reporte de préstamos"])
        fecha_inicio = st.date_input("Desde:")
        fecha_fin = st.date_input("Hasta:")

        if st.button("📄 Generar documento"):
            st.success(f"{tipo} generado del {fecha_inicio} al {fecha_fin}.")
            st.info("💾 En futuras versiones podrás descargar el PDF automáticamente.")
