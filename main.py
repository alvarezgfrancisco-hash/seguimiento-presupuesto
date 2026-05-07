def enviar_correo(archivo_excel):
    # --- CONFIGURACIÓN USANDO SECRETS ---
    remitente = st.secrets["email_usuario"]
    password = st.secrets["email_password"]
    destinatario = st.secrets["email_profe"]

    msg = MIMEMultipart()
    msg['From'] = remitente
    msg['To'] = destinatario
    msg['Subject'] = "Entrega Seguimiento Presupuesto - Automatizado"

    cuerpo = "Hola Ana, adjunto envío el presupuesto generado automáticamente desde mi app."
    msg.attach(MIMEText(cuerpo, 'plain'))

    # Adjuntar el archivo Excel
    adjunto = MIMEBase('application', 'octet-stream')
    adjunto.set_payload(archivo_excel)
    encoders.encode_base64(adjunto)
    adjunto.add_header('Content-Disposition', "attachment; filename= presupuesto.xlsx")
    msg.attach(adjunto)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(remitente, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Error técnico: {e}")
        return False
