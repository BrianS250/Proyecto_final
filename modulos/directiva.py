import streamlit as st
from modulos.conexion import obtener_conexion   # ← CORREGIDO


def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registrar reuniones, préstamos, multas y generar reportes.")

    opciones = [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Generar actas y reportes"
    ]

    seleccion = st.sidebar.radio("Seleccione una opción:", opciones)

    if seleccion == "Aplicar multas":
        pagina_multas()


def pagina_multas():

    st.header("⚠️ Aplicación de multas")

    con = obtener_conexion()
    if not con:
        st.error("❌ Error al conectar con la base de datos.")
        return
    cursor = con.cursor()

    cursor.execute("SELECT Id_Socia, Nombre FROM Socia")
    socias = cursor.fetchall()

    if not socias:
        st.warning("⚠ No hay socias registradas.")
        return

    dic_socias = {nombre: sid for sid, nombre in socias}

    socia_sel = st.selectbox("Seleccione la socia:", list(dic_socias.keys()))
    id_socia = dic_socias[socia_sel]

    cursor.execute("SELECT Id_Tipo_multa, Tipo_de_multa FROM Tipo_de_multa")
    tipos = cursor.fetchall()

    if not tipos:
        st.warning("⚠ No hay tipos de multa registrados.")
        return

    dic_tipos = {nombre: tid for tid, nombre in tipos}

    tipo_sel = st.selectbox("Tipo de multa:", list(dic_tipos.keys()))
    id_tipo = dic_tipos[tipo_sel]

    monto = st.number_input(
        "Monto de la multa ($)",
        min_value=0.0,
        step=0.50,
        format="%.2f"
    )

    fecha = st.date_input("Fecha de aplicación")
    estado = st.selectbox("Estado:", ["A pagar", "Pagada"])

    if st.button("💾 Registrar multa"):

        try:
            cursor.execute("""
                INSERT INTO Multa 
                (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Socia)
                VALUES (%s, %s, %s, %s, %s)
            """,
            (monto, fecha, estado, id_tipo, id_socia))

            con.commit()
            st.success("✔ Multa registrada correctamente.")

        except Exception as e:
            st.error(f"❌ Error registrando la multa: {e}")

    cursor.close()
    con.close()
