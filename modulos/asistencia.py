import streamlit as st

# ===============================================================
#     INTERFAZ BÁSICA DE ASISTENCIA (SIN GENERAR PDF)
# ===============================================================

def interfaz_asistencia():
    st.header("📋 Registro de asistencia del grupo")

    st.write("""
        Esta sección permitirá registrar la asistencia de las socias en cada reunión.
        Más adelante se conectará a la base de datos para guardar la asistencia real.
    """)

    # Datos de la reunión
    fecha_reunion = st.date_input("Fecha de la reunión")
    modalidad = st.selectbox("Modalidad (M/H):", ["M", "H"])

    st.subheader("📝 Lista de asistencia")
    st.info("Pronto aquí aparecerá la lista de socias para marcar presente/ausente.")

    # Botón de registro (aún sin base de datos)
    if st.button("Guardar asistencia"):
        st.success("✔ La asistencia será guardada aquí cuando activemos la base de datos.")
