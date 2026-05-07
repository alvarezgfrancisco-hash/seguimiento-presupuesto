import streamlit as st
import pandas as pd
from datetime import date
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Seguimiento Presupuesto", page_icon="💰")

st.title("💰 Seguimiento de Presupuesto")
st.write("Registra los albaranes y automatiza el envío del presupuesto.")

# 2. INICIALIZAR EL ESTADO DE DATOS (Para que no se borren al pulsar botones)
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=[
        "Fecha", "Albarán", "Trabajador", "Partida", "Gasto (€)", "Comentarios", "Foto"
    ])

# 3. FUNCIÓN PARA ENVIAR CORREO
def enviar_correo(archivo_excel):
    try:
        # Estos datos los coge de Settings > Secrets en Streamlit Cloud
        remitente = st.secrets["email_usuario"]
        password = st.secrets["email_password"]
        destinatario = st.secrets["email_profe"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Entrega Presupuesto Obra - {date.today()}"

        cuerpo = "Hola Ana,\n\nAdjunto envío el archivo Excel con el seguimiento del presupuesto generado desde mi aplicación Python."
        msg.attach(MIMEText(cuerpo, 'plain'))

        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(archivo_excel)
        encoders.encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', "attachment; filename= presupuesto.xlsx")
        msg.attach(adjunto)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error detallado: {e}")
        return False

# 4. FORMULARIO DE ENTRADA
with st.form("formulario_gastos", clear_on_submit=True):
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

    submit_data = st.form_submit_button("➕ Añadir al registro local")

if submit_data:
    if n_albaran and trabajador:
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
        st.success("Registro añadido correctamente a la tabla de abajo.")
    else:
        st.error("Rellena al menos el Número de albarán y el Trabajador.")

st.divider()

# 5. TABLA Y BOTONES DE ACCIÓN
st.subheader("📋 Registros actuales")
st.dataframe(st.session_state.datos, use_container_width=True)

# Preparamos el Excel por si acaso hay datos
if not st.session_state.datos.empty:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        st.session_state.datos.to_excel(writer, index=False)
    excel_data = output.getvalue()

    # Botones finales
    st.download_button(
        label="📥 Descargar Excel",
        data=excel_data,
        file_name="presupuesto.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    if st.button("🚀 Enviar directamente a la profe"):
        with st.spinner("Enviando correo..."):
            if enviar_correo(excel_data):
                st.success("✅ ¡Correo enviado con éxito a la profesora!")
            else:
                st.error("❌ Falló el envío. Revisa que tus Secrets y el código de 16 letras sean correctos.")
else:
    st.info("Añade algún registro para poder descargar o enviar el Excel.")
