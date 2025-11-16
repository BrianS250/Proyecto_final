import streamlit as st
from datetime import date
from modulos.config.conexion import obtener_conexion

# ============================================================
# 👩‍💼 PANEL DE LA DIRECTIVA DEL GRUPO
# ============================================================
def interfaz_directiva():
    st.title("👩‍💼 Panel de la Directiva del Grupo")
    st.write("Registra reuniones, préstamos, pagos, multas y genera reportes de tu grupo.")

    opcion = st.sidebar.radio(
        "Selecciona una opción:",
        [
            "📅 Registrar reunión y asistencia",
            "💰 Registrar préstamo",
            "💵 Registrar pago",
            "⚖️ Aplicar multa",
            "📑 Generar actas y reportes"
        ]
    )

    if opcion == "📅 Registrar reunión y asistencia":
        registrar_reunion()
    elif opcion == "💰 Registrar préstamo":
        registrar_prestamo()
    elif opcion == "💵 Registrar pago":
        registrar_pago()
    elif opcion == "⚖️ Aplicar multa":
        aplicar_multa()
    elif opcion == "📑 Generar actas y reportes":
        generar_reporte()

# ============================================================
# 📅 REGISTRAR REUNIÓN Y ASISTENCIA
# ============================================================
def registrar_reunion():
    st.subheader("📅 Registrar reunión y asistencia")
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT Id_Grupo, Nombre_grupo FROM Grupo")
    grupos = cur.fetchall()

    if not grupos:
        st.warning("⚠️ No hay grupos registrados.")
        return

    grupo = st.selectbox("Selecciona el grupo:", [f"{g[0]} - {g[1]}" for g in grupos])
    fecha = st.date_input("Fecha de la reunión", value=date.today())
    tema = st.text_input("Tema o motivo de la reunión")
    asistentes = st.text_area("Lista de asistentes (separados por coma)")
    observaciones = st.text_area("Observaciones generales")

    if st.button("💾 Guardar reunión"):
        try:
            id_grupo = grupo.split(" - ")[0]
            cur.execute("""
                INSERT INTO Reuniones (Id_Grupo, Fecha, Tema, Asistentes, Observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_grupo, fecha, tema, asistentes, observaciones))
            con.commit()
            st.success("✅ Reunión registrada correctamente.")
        except Exception as e:
            st.error(f"❌ Error al registrar la reunión: {e}")
        finally:
            cur.close()
            con.close()

# ============================================================
# 💰 REGISTRAR PRÉSTAMO
# ============================================================
def registrar_prestamo():
    st.subheader("💰 Registrar nuevo préstamo")
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT Id_Grupo, Nombre_grupo FROM Grupo")
    grupos = cur.fetchall()

    if not grupos:
        st.warning("⚠️ No hay grupos disponibles.")
        return

    grupo = st.selectbox("Selecciona el grupo:", [f"{g[0]} - {g[1]}" for g in grupos])
    nombre_socio = st.text_input("Nombre del socio beneficiado")
    monto = st.number_input("Monto del préstamo ($)", min_value=0.0, step=0.01)
    tasa_interes = st.number_input("Tasa de interés (%)", min_value=0.0, step=0.1)
    fecha_prestamo = st.date_input("Fecha del préstamo", value=date.today())
    plazo = st.number_input("Plazo (en meses)", min_value=1, step=1)

    if st.button("💾 Registrar préstamo"):
        try:
            id_grupo = grupo.split(" - ")[0]
            cur.execute("""
                INSERT INTO Prestamo (Id_Grupo, Nombre_socio, Monto, Tasa_interes, Fecha_prestamo, Plazo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_grupo, nombre_socio, monto, tasa_interes, fecha_prestamo, plazo))
            con.commit()
            st.success("✅ Préstamo registrado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al registrar préstamo: {e}")
        finally:
            cur.close()
            con.close()

# ============================================================
# 💵 REGISTRAR PAGO
# ============================================================
def registrar_pago():
    st.subheader("💵 Registrar pago")
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT Id_Prestamo, Nombre_socio FROM Prestamo")
    prestamos = cur.fetchall()

    if not prestamos:
        st.warning("⚠️ No hay préstamos registrados.")
        return

    prestamo = st.selectbox("Selecciona préstamo:", [f"{p[0]} - {p[1]}" for p in prestamos])
    monto_pago = st.number_input("Monto pagado ($)", min_value=0.0, step=0.01)
    fecha_pago = st.date_input("Fecha del pago", value=date.today())
    descripcion = st.text_area("Descripción del pago")

    if st.button("💾 Registrar pago"):
        try:
            id_prestamo = prestamo.split(" - ")[0]
            cur.execute("""
                INSERT INTO Pago (Id_Prestamo, Fecha_pago, Monto_pago, Descripcion)
                VALUES (%s, %s, %s, %s)
            """, (id_prestamo, fecha_pago, monto_pago, descripcion))
            con.commit()
            st.success("✅ Pago registrado correctamente.")
        except Exception as e:
            st.error(f"❌ Error al registrar pago: {e}")
        finally:
            cur.close()
            con.close()

# ============================================================
# ⚖️ APLICAR MULTA
# ============================================================
def aplicar_multa():
    st.subheader("⚖️ Aplicar multa")
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("SELECT Id_Grupo, Nombre_grupo FROM Grupo")
    grupos = cur.fetchall()

    if not grupos:
        st.warning("⚠️ No hay grupos disponibles.")
        return

    grupo = st.selectbox("Selecciona el grupo:", [f"{g[0]} - {g[1]}" for g in grupos])
    nombre_socio = st.text_input("Nombre del socio sancionado")
    motivo = st.text_area("Motivo de la multa")
    monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.01)
    fecha_multa = st.date_input("Fecha de la multa", value=date.today())

    if st.button("💾 Registrar multa"):
        try:
            id_grupo = grupo.split(" - ")[0]
            cur.execute("""
                INSERT INTO Multa (Id_Grupo, Nombre_socio, Motivo, Monto, Fecha_multa)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_grupo, nombre_socio, motivo, monto, fecha_multa))
            con.commit()
            st.success("✅ Multa registrada correctamente.")
        except Exception as e:
            st.error(f"❌ Error al registrar multa: {e}")
        finally:
            cur.close()
            con.close()

# ============================================================
# 📑 GENERAR ACTAS Y REPORTES
# ============================================================
def generar_reporte():
    st.subheader("📑 Generar actas y reportes")
    st.info("Aquí podrás generar reportes consolidados de reuniones, préstamos, pagos y multas.")
    st.warning("⚠️ Módulo en desarrollo: pronto podrás exportar los reportes en PDF o Excel.")
