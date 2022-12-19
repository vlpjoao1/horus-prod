import smtplib
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect

# Create your views here.
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, RedirectView

from config import settings
from core.login.forms import ResetPasswordForm, ChangePasswordForm
from core.user.models import User


class LoginFormView(LoginView):
    template_name = 'login/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar sesión'
        return context


class LoginFormView2(FormView):
    form_class = AuthenticationForm
    template_name = 'login/login.html'
    success_url = reverse_lazy('dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Iniciar sesión'
        return context


class LogoutRedirectView(RedirectView):
    pattern_name = 'accounts:login'

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return super().dispatch(request, *args, **kwargs)



class ResetPasswordView(FormView):
    form_class = ResetPasswordForm
    template_name = 'login/resetpwd.html'
    success_url = reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def send_email_reset_pwd(self, user):
        data = {}
        try:
            """Si debug esta en FALSE obtiene el DOMAIN si esta en TRUE que obtenga el HTTP_HOST"""
            URL = settings.DOMAIN if not settings.DEBUG else self.request.META['HTTP_HOST']

            user.token = uuid.uuid4()
            user.save()
            # Establecemos conexion con el servidor smtp de gmail
            # Conectamos al servidor
            mailServer = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            """Ehlo es la etapa del protocolo smtp en la que un servidor se presenta entre si. Y verifica
             que no hay errores en el proceso"""
            # print(mailServer.ehlo())
            """TLS sirve para mejorar la seguridad de las conexiones SMTP igual que SSL y evitar hackeos"""
            mailServer.starttls()
            # print(mailServer.ehlo())
            mailServer.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

            email_to = user.email
            # Construimos el mensaje simple
            # mensaje = MIMEText("""Este es el mensaje de las narices""")
            # Construimos el mensaje que pueda enviar tambien HTML y archivos
            mensaje = MIMEMultipart()
            mensaje['From'] = settings.EMAIL_HOST_USER
            mensaje['To'] = email_to
            mensaje['Subject'] = 'Reseteo de contraseña'

            # convertimos un template en un string (esto es una funcion de django) y le enviamos parametros
            content = render_to_string('login/send_email.html',
                                       # variables que le pasaremos al template
                                       {'link_resetpwd': 'http://{}/login/change/password/{}/'.format(URL, str(user.token)),
                                        #Pasamos la url y el token del usuario
                                        'link_home': 'http://{}'.format(URL),
                                        'user': user
                                        })
            # Adjuntamos el archivo y especificamos su tipo
            mensaje.attach(MIMEText(content, 'html'))

            # Envio del mensaje
            mailServer.sendmail(settings.EMAIL_HOST_USER,
                                email_to,
                                mensaje.as_string())
        except Exception as e:
            data['error'] = str(e)
        return data

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = ResetPasswordForm(request.POST)  # self.get_form()
            if form.is_valid():
                user = form.get_user()
                #print(self.request.META['HTTP_HOST'])
                data = self.send_email_reset_pwd(user)
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        # Para serializar los elementos que no sean diccionaros, debes establecer safe=False
        # Ya que estamos enviando una lista de diccionarios, no un diccionario solo
        return JsonResponse(data, safe=False)

    def form_valid(self, form):
        pass
        # login(self.request, form.get_user())
        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reseteo de contraseña'
        return context


class ChangePasswordView(FormView):
    form_class = ChangePasswordForm
    template_name = 'login/changepwd.html'
    success_url = reverse_lazy('dashboard')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    """Moddificamos el metodo get, para validar que la url del cambio de contrasena sea valido"""
    def get(self, request, *args, **kwargs):
        #asi llamamos a la variable en la url
        token = self.kwargs['token']
        #si existe un usuario con ese token que viene del correo, damos paso a la vista
        if User.objects.filter(token=token).exists():
            return super().get(request, *args , **kwargs)
        #Si no existe lo mandamos a la pagina principal
        return HttpResponseRedirect('/')

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            form = self.form_class(request.POST)
            if form.is_valid():
                #este token viene de los parametros de la url
                user = User.objects.get(token=self.kwargs['token'])
                user.set_password(request.POST['password'])
                #cambiamos el token para que el correo no se vuelva a utilziar
                user.token = uuid.uuid4()
                user.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        # Para serializar los elementos que no sean diccionaros, debes establecer safe=False
        # Ya que estamos enviando una lista de diccionarios, no un diccionario solo
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reseteo de contraseña'
        context['login_url'] = settings.LOGIN_URL
        return context
