import streamlit as st
from datetime import date
from modulos.configuracion.conexion import obtener_conexion


def interfaz_directiva():
    st.title("👩‍💼 Panel de Directiva del Grupo")
    st.write("Registra reuniones, préstamos, multas y reportes del grupo.")

    opcion = st.sidebar.radio("Selecciona una opción:", [
        "Registrar reunión y asistencia",
        "Registrar préstamos o pagos",
        "Aplicar multas",
        "Ver multas registradas",
        "Generar actas y reportes"
    ])

    # -------------------------------------------------------------------------
    # ⚠️ OPCIÓN: APLICAR MULTAS
    # -------------------------------------------------------------------------
    if opcion == "Aplicar multas":
        st.subheader("⚠️ Aplicación de multas")

        id_usuario = st.number_input("ID del miembro sancionado (Id_Usuario)", min_value=1, step=1)
        id_tipo = st.number_input("ID del tipo de multa (Id_Tipo_multa)", min_value=1, step=1)
        monto = st.number_input("Monto de la multa ($)", min_value=0.0, step=0.5)
        estado = st.selectbox("Estado de la multa", ["Pendiente", "Pagada", "Condonada"])
        fecha = date.today()

        if st.button("Registrar multa"):
            try:
                con = obtener_conexion()
                cursor = con.cursor()

                cursor.execute("""
                    INSERT INTO Multa (Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Usuario)
                    VALUES (%s, %s, %s, %s, %s)
                """, (monto, fecha, estado, id_tipo, id_usuario))

                con.commit()
                st.success(f"✅ Multa registrada correctamente para el usuario ID {id_usuario}.")
            except Exception as e:
                st.error(f"❌ Error al registrar la multa: {e}")
            finally:
                con.close()

    # -------------------------------------------------------------------------
    # 📊 OPCIÓN: VER MULTAS REGISTRADAS
    # -------------------------------------------------------------------------
    elif opcion == "Ver multas registradas":
        st.subheader("📋 Multas registradas")

        try:
            con = obtener_conexion()
            cursor = con.cursor()
            cursor.execute("SELECT Id_Multa, Monto, Fecha_aplicacion, Estado, Id_Tipo_multa, Id_Usuario FROM Multa")
            resultados = cursor.fetchall()

            if resultados:
                import pandas as pd
                df = pd.DataFrame(resultados, columns=["ID", "Monto", "Fecha", "Estado", "Tipo", "Usuario"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay multas registradas actualmente.")
        except Exception as e:
            st.error(f"❌ Error al consultar las multas: {e}")
        finally:
            con.close()
