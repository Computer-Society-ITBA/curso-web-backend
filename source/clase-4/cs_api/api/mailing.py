# Mailing
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.tokens import default_token_generator

# Envía el email de confirmación
def send_confirmation_email(user, request):
    # Obtiene el link al sitio
    current_site = get_current_site(request)
    # Genera los templates
    plaintext = get_template('emailVerify.txt')
    html_template = get_template('emailVerify.html')
    # Le pasa los datos a cada template para que la customize
    data = {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user), # Genera el token
    }
    text_content = plaintext.render(data)
    html_content = html_template.render(data)
    # Seteamos asunto
    mail_subject = 'Verificá tu Cuenta'
    # Definimos el mail con contenido texto
    msg = EmailMultiAlternatives(mail_subject, text_content, to=[user.email])
    # Agregamos versión HTML
    msg.attach_alternative(html_content, "text/html")
    # Enviamos
    msg.send()