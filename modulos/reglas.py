import streamlit as st
from modulos.conexion import obtener_conexion


# ---------------------------------------------------------
# 📘 GESTIÓN DE REGLAS INTERNAS
# ---------------------------------------------------------
def gestionar_reglas():
    st.subheader("📘 Reglas internas del grupo")

    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    # Buscar si ya existen reglas registradas
    cursor.execute("SELECT * FROM reglas_grupo ORDER BY id_regla DESC LIMIT 1")
    reglas = cursor.fetchone()

    if reglas:
        st.success("Reglas existentes encontradas.")
        mostrar_reglas(reglas)
    else:
        st.warning("No hay reglas registradas para este grupo.")
        crear_reglas()

    cursor.close()
    con.close()



# ---------------------------------------------------------
# 📝 CREAR REGLAS INTERNAS
# ---------------------------------------------------------
def crear_reglas():
    st.info("Complete el formulario para registrar las reglas internas del grupo.")

    with st.form("form_reglas"):
        nombre_grupo = st.text_input("Nombre del grupo de ahorro")
        comunidad = st.text_input("Nombre de la comunidad")
        fecha_formacion = st.date_input("Fecha de formación")

        multa = st.number_input("Multa por inasistencia ($)", min_value=0.0)
        ahorro_minimo = st.number_input("Ahorro mínimo ($)", min_value=0.0)
        interes = st.number_input("Interés por cada $10 prestados (%)", min_value=0.0)
        prestamo_maximo = st.number_input("Monto máximo de préstamo", min_value=0.0)
        plazo_maximo = st.number_input("Plazo máximo del préstamo (meses)", min_value=1)

        ciclo_inicio = st.date_input("Inicio del ciclo")
        ciclo_fin = st.date_input("Fin del ciclo")

        meta = st.text_area("Meta social")
        otras = st.text_area("Otras reglas")

        enviar = st.form_submit_button("💾 Guardar reglas")

        if enviar:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                INSERT INTO reglas_grupo
                (Id_Grupo, nombre_grupo, nombre_comunidad, fecha_formacion, multa_inasistencia,
                ahorro_minimo, interes_por_10, prestamo_maximo, plazo_maximo, ciclo_inicio, ciclo_fin,
                meta_social, otras_reglas)
                VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                nombre_grupo, comunidad, fecha_formacion, multa, ahorro_minimo, interes,
                prestamo_maximo, plazo_maximo, ciclo_inicio, ciclo_fin, meta, otras
            ))

            con.commit()
            con.close()

            st.success("Reglas internas registradas correctamente.")
            st.rerun()



# ---------------------------------------------------------
# 👁 MOSTRAR REGLAS INTERNAS
# ---------------------------------------------------------
def mostrar_reglas(reglas):
    st.write("### 📌 Información general del grupo")
    st.write(f"**Nombre del grupo:** {reglas['nombre_grupo']}")
    st.write(f"**Comunidad:** {reglas['nombre_comunidad']}")
    st.write(f"**Fecha de formación:** {reglas['fecha_formacion']}")

    st.write("### 💰 Ahorros y multas")
    st.write(f"- Multa por inasistencia: **${reglas['multa_inasistencia']}**")
    st.write(f"- Ahorro mínimo obligatorio: **${reglas['ahorro_minimo']}**")

    st.write("### 💵 Reglas de préstamo")
    st.write(f"- Interés por cada $10 prestados: **{reglas['interes_por_10']}%**")
    st.write(f"- Monto máximo del préstamo: **${reglas['prestamo_maximo']}**")
    st.write(f"- Plazo máximo: **{reglas['plazo_maximo']} meses**")

    st.write("### 🔁 Ciclo del grupo")
    st.write(f"- Inicio del ciclo: {reglas['ciclo_inicio']}")
    st.write(f"- Fin del ciclo: {reglas['ciclo_fin']}")

    st.write("### 🎯 Meta social")
    st.write(reglas["meta_social"])

    st.write("### 📄 Otras reglas")
    st.write(reglas["otras_reglas"])

