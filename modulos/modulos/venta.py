import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_venta():
    st.title("🧾 Registro de Ventas")

    # -------------------------------------------------------
    # 🧩 Formulario para registrar una venta
    # -------------------------------------------------------
    with st.form("form_venta"):
        producto = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio_unitario = st.number_input("Precio unitario ($)", min_value=0.01, step=0.01)
        total = cantidad * precio_unitario

        st.write(f"💰 Total calculado: **${total:.2f}**")
        enviar = st.form_submit_button("✅ Registrar venta")

        if enviar:
            con = obtener_conexion()
            if not con:
                st.error("❌ No se pudo conectar a la base de datos.")
                return
            
            try:
                cursor = con.cursor()
                query = "INSERT INTO Venta (Producto, Cantidad, PrecioUnitario, Total) VALUES (%s, %s, %s, %s)"
                cursor.execute(query, (producto, cantidad, precio_unitario, total))
                con.commit()
                st.success("✅ Venta registrada correctamente.")
            except Exception as e:
                st.error(f"⚠️ Error al registrar la venta: {e}")
            finally:
                con.close()

    st.divider()

    # -------------------------------------------------------
    # 📋 Mostrar el historial de ventas registradas
    # -------------------------------------------------------
    st.subheader("📊 Ventas registradas")

    con = obtener_conexion()
    if con:
        try:
            cursor = con.cursor()
            cursor.execute("SELECT Id_Venta, Producto, Cantidad, PrecioUnitario, Total FROM Venta ORDER BY Id_Venta DESC")
            ventas = cursor.fetchall()

            if ventas:
                st.table(ventas)
                total_general = sum([fila[4] for fila in ventas])
                st.markdown(f"### 💵 Total acumulado: **${total_general:.2f}**")
            else:
                st.info("🕓 Aún no hay ventas registradas.")
        except Exception as e:
            st.error(f"⚠️ Error al obtener los registros: {e}")
        finally:
            con.close()
    else:
        st.error("⚠️ No se pudo conectar a la base de datos.")
