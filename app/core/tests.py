from config.wsgi import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.template.loader import render_to_string

from config import settings
# Para poder usar el modelo de usuario debemos importar django WSGI
from core.user.models import User


def send_email():
    try:
        # Establecemos conexion con el servidor smtp de gmail
        # Conectamos al servidor
        mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        """Ehlo es la etapa del protocolo smtp en la que un servidor se presenta entre si. Y verifica
         que no hay errores en el proceso"""
        print(mailServer.ehlo())
        """TLS sirve para mejorar la seguridad de las conexiones SMTP igual que SSL y evitar hackeos"""
        mailServer.starttls()
        print(mailServer.ehlo())
        mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        print('Conectado...')

        email_to = 'esdeciencia@gmail.com'
        # Construimos el mensaje simple
        # mensaje = MIMEText("""Este es el mensaje de las narices""")
        # Construimos el mensaje que pueda enviar tambien HTML y archivos
        mensaje = MIMEMultipart()
        mensaje['From'] = settings.EMAIL_HOST_USER
        mensaje['To'] = email_to
        mensaje['Subject'] = "Tienes un correo"

        # convertimos un template en un string (esto es una funcion de django) y le enviamos parametros
        content = render_to_string('send_email.html', {'user': User.objects.get(pk=1)})
        # Adjuntamos el archivo y especificamos su tipo
        mensaje.attach(MIMEText(content, 'html'))

        # Envio del mensaje
        mailServer.sendmail(settings.EMAIL_HOST_USER,
                            email_to,
                            mensaje.as_string())
    except Exception as e:
        print(e)


send_email()
