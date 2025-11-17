import streamlit as st

def interfaz_directiva():
    st.title("👨‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("Selecciona una opción:", opciones)

    if seleccion == "Registrar reunión y asistencia":
        pagina_reunion()

    elif seleccion == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif seleccion == "Aplicar multas":
        pagina_multas()

    elif seleccion == "Generar actas y reportes":
        pagina_reportes()


# ======== PÁGINAS ========

def pagina_reunion():
    st.header("📅 Registro de reunión")
    fecha = st.date_input("Fecha de la reunión")
    tema = st.text_input("Tema principal")
    asistentes = st.text_input("Lista de asistentes (separados por comas)")
    if st.button("Guardar reunión"):
        st.success("Reunión registrada correctamente.")


def pagina_prestamos():
    st.header("💰 Registro de préstamos o pagos")
    tipo = st.selectbox("Tipo de registro", ["Préstamo", "Pago"])
    descripcion = st.text_area("Descripción")
    if st.button("Guardar movimiento"):
        st.success("Movimiento registrado correctamente.")


def pagina_multas():
    st.header("⚠️ Aplicación de multas")
    miembro = st.text_input("Nombre del miembro sancionado")
    motivo = st.text_area("Motivo de la multa")
    monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)
    if st.button("Registrar multa"):
        st.success("Multa registrada correctamente.")


def pagina_reportes():
    st.header("📊 Generar actas y reportes")
    st.info("Aquí podrás generar reportes del grupo.")


