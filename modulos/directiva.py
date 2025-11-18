import streamlit as st
from modulos.config.conexion import obtener_conexion


# ============================================================
#  PANEL PRINCIPAL DE DIRECTIVA
# ============================================================

def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registrar reuniones, préstamos, multas y generar reportes.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("📌 Seleccione una opción:", opciones)

    if seleccion == "Registrar reunión y asistencia":
        pagina_reunion()

    elif seleccion == "Registrar préstamos o pagos":
        pagina_prestamos()

    elif seleccion == "Aplicar multas":
        pagina_multas()

    elif seleccion == "Generar actas y reportes":
        pagina_reportes()



# ============================================================
#  PÁGINA DE REUNIÓN
# ============================================================

def pagina_reunion():
    st.header("📅 Registro de reunión")

    fecha = st.date_input("Fecha de la reunión")
    tema = st.text_input("Tema principal")
    asistentes = st.text_area("Lista de asistentes (separados por comas)")

    if st.button("💾 Guardar reunión"):
        st.success("✔ Reunión registrada correctamente (aún no conectada a MySQL).")



# ============================================================
#  PÁGINA DE PRÉSTAMOS / PAGOS
# ============================================================

def pagina_prestamos():
    st.header("💰 Registro de préstamos o pagos")

    tipo = st.selectbox("Tipo de registro", ["Préstamo", "Pago"])
    descripcion = st.text_area("Descripción del movimiento")

    if st.button("💾 Guardar movimiento"):
        st.success("✔ Movimiento registrado correctamente (aún no conectado a MySQL).")



# ============================================================
#  PÁGINA DE MULTAS (FUNCIONAL CON MYSQL)
# ============================================================

def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    # Conectar con MySQL
    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con MySQL.")
        return

    cursor = con.cursor()

    # ---------------------------------------------------------
    # Cargar SOCIAS desde MySQL
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
        socias = cursor.fetchall()
    except Exception as e:
        st.error(f"❌ Error cargando socias: {e}")
        return

    if not socias:
        st.warning("⚠ No hay socias registradas en la tabla <Socia>.")
        return

    dic_socias = {nombre: sid for sid, nombre in socias}

    socia_sel = st.selectbox("Seleccione la socia:", list(dic_socias.keys()))
    id_socia = dic_socias[socia_sel]

    # ---------------------------------------------------------
    # Cargar Tipos de Multa
    # ---------------------------------------------------------
    try:
        cursor.execute("SELECT Id_Tipo_multa, Nombre_tipo FROM Tipo_de_multa")
        tipos = cursor.fetchall()
    except Exception as e:
        st.error(f"❌ Error cargando tipos de multa: {e}")
        return

    if not tipos:
        st.warning("⚠ No existen tipos de multa registrados.")
        return

    dic_tipos = {nombre: tid for tid, nombre in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", list(dic_tipos.keys()))
    id_tipo = dic_tipos[tipo_sel]

    # ---------------------------------------------------------
    # Datos adicionales de la multa
    # ---------------------------------------------------------
    monto = st.number_input("Monto de la multa ($)", min_value=0.00)
    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado de la multa:", ["Pendiente", "Pagada"])

    id_asistencia = st.number_input("ID Asistencia (opcional)", min_value=0, step=1)
    id_prestamo = st.number_input("ID Préstamo (opcional)", min_value=0, step=1)

    # ---------------------------------------------------------
    # BOTÓN PARA GUARDAR
    # ---------------------------------------------------------
    if st.button("💾 Registrar multa"):
        try:
            cursor.execute("""
                INSERT INTO Multa 
                (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia, Id_Asistencia, Id_Préstamo)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                monto,
                fecha,
                estado,
                id_tipo,
                id_socia,
                id_asistencia if id_asistencia != 0 else None,
                id_prestamo if id_prestamo != 0 else None
            ))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error guardando multa: {e}")

    cursor.close()
    con.close()



# ============================================================
#  PÁGINA DE REPORTES (BÁSICO)
# ============================================================

def pagina_reportes():
    st.header("📊 Actas y Reportes del Grupo")
    st.info("Aquí podrás generar reportes financieros, de asistencia y de multas.")

