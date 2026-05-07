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

# Intentar cargar logo si existe (opcional)
# st.image("logo.png", width=200)

st.title("💰 Seguimiento de Presupuesto")
st.write("Registra los albaranes y automatiza el envío del presupuesto.")

# 2. INICIALIZAR EL ESTADO DE DATOS
if 'datos' not in st.session_state:
    st.session_state.datos = pd.DataFrame(columns=[
        "Fecha", "Albarán", "Trabajador", "Partida", "Gasto (€)", "Comentarios", "Foto"
    ])

# 3. FUNCIÓN PARA ENVIAR CORREO (Usa los Secrets de Streamlit)
def enviar_correo(archivo_excel):
    try:
        remitente = st.secrets["email_usuario"]
        password = st.secrets["email_password"]
        destinatario = st.secrets["email_profe"]

        msg = MIMEMultipart()
        msg['From'] = remitente
        msg['To'] = destinatario
        msg['Subject'] = f"Entrega Presupuesto Obra - {date.today()}"

        cuerpo = "Hola Ana,\n\nAdjunto envío el archivo Excel con el seguimiento del presupuesto generado desde la aplicación Python."
        msg.attach(MIMEText(cuerpo, 'plain'))

        # Preparar el archivo adjunto
        adjunto = MIMEBase('application', 'octet-stream')
        adjunto.set_payload(archivo_excel)
        encoders.encode_base64(adjunto)
        adjunto.add_header('Content-Disposition', "attachment; filename= presupuesto.xlsx")
        msg.attach(adjunto)

        # Conexión al servidor Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error al enviar: {e}")
        return False

# 4. FORMULARIO DE ENTRADA (Mínimos exigidos)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        fecha = st.date_input("Fecha", date.today())
        n_albaran = st.text_input("Número de albarán", placeholder="Ej: ALB-2026-01")
        trabajador = st.text_input("Nombre del trabajador")
    with col2:
        partida = st.selectbox("Partida del presupuesto asociada:", [
            "Material Eléctrico", "Mano de Obra", "Herramientas", "Desplazamientos", "Otros"
        ])
        gastos = st.number_input("Gastos de esa partida (€)", min_value=0.0, step=0.01)
    
    comentarios = st.text_area("Comentarios")
    foto = st.file_uploader("Subir foto del albarán (Nota Extra 📸)", type=["jpg", "png", "pdf"])

    if st.button("➕ Añadir al registro local"):
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
            st.error("Por favor, rellena Albarán, Trabajador e Importe")

st.divider()

# 5. VISUALIZACIÓN DE TAB
