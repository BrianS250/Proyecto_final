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

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    # ------------------------------------
    # Cargar empleados (usuarios del sistema)
    # ------------------------------------
    cursor.execute("SELECT Id_Empleado, Usuario FROM Empleado")
    empleados = cursor.fetchall()

    if not empleados:
        st.warning("⚠ No hay empleados registrados.")
        return

    dic_empleados = {nombre: eid for eid, nombre in empleados}

    empleado_sel = st.selectbox("Empleado sancionado:", list(dic_empleados.keys()))
    id_empleado = dic_empleados[empleado_sel]

    # ------------------------------------
    # Cargar tipos de multa
    # ------------------------------------
    cursor.execute("SELECT Id_Tipo_multa, Nombre_tipo FROM Tipo_de_multa")
    tipos = cursor.fetchall()

    if not tipos:
        st.warning("⚠ No hay tipos de multa configurados.")
        return

    dic_tipos = {nombre: tid for tid, nombre in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", list(dic_tipos.keys()))
    id_tipo = dic_tipos[tipo_sel]

    monto = st.number_input("Monto ($)", min_value=0.00)
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["Pendiente", "Pagada"])

    # Opcionales
    id_asistencia = st.number_input("ID Asistencia (opcional)", min_value=0, step=1)
    id_prestamo = st.number_input("ID Préstamo (opcional)", min_value=0, step=1)

    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa 
                (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Usuario, Id_Asistencia, Id_Préstamo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                monto,
                fecha,
                estado,
                id_tipo,
                id_empleado,  # CORREGIDO
                id_asistencia if id_asistencia != 0 else None,
                id_prestamo if id_prestamo != 0 else None
            ))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error: {e}")

    cursor.close()
    con.close()



def pagina_reportes():
    st.header("📊 Generar actas y reportes")
    st.info("Aquí podrás generar reportes del grupo.")

