import streamlit as st
import pandas as pd
from datetime import date
import io

# Configuración de página
st.set_page_config(page_title="Seguimiento Presupuesto", page_icon="💰")

st.title("💰 Seguimiento de Presupuesto")
st.write("Registra los albaranes y gastos de la obra.")

# Inicializar datos
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=[
        "Fecha", "Albarán", "Trabajador", "Partida", "Gasto (€)", "Comentarios", "Foto"
    ])

# Formulario (siguiendo tu estilo visual)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", date.today())
        n_albaran = st.text_input("Número de albarán")
        trabajador = st.text_input("Nombre del trabajador")
    with col2:
        partida = st.selectbox("Partida del presupuesto asociada:", [
            "Material Eléctrico", "Mano de Obra", "Herramientas", "Desplazamientos", "Otros"
        ])
        gastos = st.number_input("Gastos de esa partida (€)", min_value=0.0, step=0.01)
    
    comentarios = st.text_area("Comentarios")
    foto = st.file_uploader("Subir foto del albarán (Nota Extra 📸)", type=["jpg", "png", "pdf"])

    if st.button("Añadir al registro local"):
        if n_albaran and trabajador and gastos > 0:
            nueva_fila = {
                "Fecha": fecha.strftime("%Y/%m/%d"),
                "Albarán": n_albaran,
                "Trabajador": trabajador,
                "Partida": partida,
                "Gasto (€)": gastos,
                "Comentarios": comentarios,
                "Foto": "✅ Adjunta" if foto else "❌ No"
            }
            st.session_state.datos = pd.concat([st.session_state.datos, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.success("Añadido correctamente")
        else:
            st.error("Rellena Albarán, Trabajador e Importe")

st.divider()
st.subheader("Registros actuales")
st.dataframe(st.session_state.datos, use_container_width=True)

# Botón Excel
if not st.session_state.datos.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.datos.to_excel(writer, index=False)
    st.download_button(label="📥 Descargar Excel para enviar", data=output.getvalue(), file_name="presupuesto.xlsx")
