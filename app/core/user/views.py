from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from core.erp.mixins import IsSuperuserMixin, ValidatePermissionRequiredMixin
from core.user.forms import UserForm, UserProfileForm
from core.user.models import User


class UserListView(ValidatePermissionRequiredMixin, ListView):
    permission_required = 'view_user'
    model = User
    template_name = 'user/list.html'

    # decoradores: Son funciones que añaden funcionalidades a otras funciones.
    # ej: si queremos añadir una validación al metodo dispatch, podemos usar un decorador.

    # dispatch: Es un metodo que se ejecuta al principio de la llamada de una vista. Se encarga de
    # redireccionar a la peticion que se haga, sea post o get.
    # @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in User.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
            # data = User.objects.get(pk=request.POST['id']).toJson()
        except Exception as e:
            data['error'] = str(e)
        # Para serializar los elementos que no sean diccionaros, debes establecer safe=False
        # Ya que estamos enviando una lista de diccionarios, no un diccionario solo
        return JsonResponse(data, safe=False)

    # Se puede listar solo con modelo y template_name. Hace automaticamente un objects.all
    # Puedes enviar la consulta desde aquí o usar el get_queryset()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Usuarios'
        context['create_url'] = reverse_lazy('user:user_createview')
        context['entity'] = 'Usuarios'
        context['list_url'] = reverse_lazy('user:user_listview')
        return context


"""
    Estas vistas se pueden usar solamente poniendo el modelo, el formulario y el template.
    Sobreescribir los métodos, ya es más para personalización.
"""


class UserCreateView(ValidatePermissionRequiredMixin, CreateView):
    permission_required = 'add_user'
    model = User
    form_class = UserForm
    template_name = 'user/create.html'
    # Reverse_lazy devuelve la cadena de texto de esa url
    success_url = reverse_lazy('user:user_listview')
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear un Usuario'
        context['entity'] = 'Usuarios'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

    def post(self, request, *kargs, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.form_class(request.POST, request.FILES)
                data = form.save()
                # if form.is_valid():
                #     form.save()
                # else:
                #     data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)
        """Este codigo sería para retornar los errores sin ajax"""
        # form = self.form_class(request.POST)
        # if form.is_valid():
        #     form.save()
        #     return HttpResponseRedirect(self.success_url)
        # #self.object es el objeto que se está creando. Si el objeto no se ha creado
        # #el valor deberá ser None, es decir, si ha ocurrido un error.
        # self.object = None
        # context = self.get_context_data(**kwargs)
        # context['form'] = form
        # # si queremos devolver los datos del formulario a la vista, podemos hacerlo así
        # # Enviando el formulario con su instancia de request.POST
        # return render(request, self.template_name, context)


class UserUpdateView(ValidatePermissionRequiredMixin, UpdateView):
    permission_required = 'change_user'
    model = User
    form_class = UserForm
    template_name = 'user/create.html'
    success_url = reverse_lazy('user:user_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Como object no tiene un valor, tenemos que asignarselo
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de un Usuario'
        context['entity'] = 'Usuarios'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class UserDeleteView(ValidatePermissionRequiredMixin, DeleteView):
    permission_required = 'delete_user'
    model = User
    template_name = 'user/delete.html'
    success_url = reverse_lazy('user:user_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # lo creamos en el dispatch porque al sobreescribir el metodo POST no existe de una el self.object
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    # si sobreescribimos el método post, la variable self.object aun no tiene un valor,por lo qe
    # debemos asignarle el valor a self.object en el dispatch
    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de un Usuario'
        context['entity'] = 'Usuarios'
        context['list_url'] = self.success_url
        context['action'] = 'delete'
        return context


class UserChangeGroup(View):

    def get(self, request, *args, **kwargs):
        try:
            # con request.session trabajamos con las variables de sesion
            # https: // docs.djangoproject.com / en / 3.0 / ref / settings /  # sessions
            request.session['group'] = Group.objects.get(pk=self.kwargs['pk'])
            # le pasamos la instancia del grupo a la sesion
        except:
            pass
        return HttpResponseRedirect(reverse_lazy('dashboard'))


class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'user/profile.html'
    success_url = reverse_lazy('dashboard')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Como object no tiene un valor, tenemos que asignarselo
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    """Como no estamos enviando el objeto a traves de la url, lo definimos aqui para que no haya problemas"""

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                form = self.get_form()
                data = form.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de perfil'
        context['entity'] = 'Perfil'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class UserChangePasswordView(FormView):
    model = User
    # Este es un formulario propio de Django
    form_class = PasswordChangeForm
    template_name = 'user/change_password.html'
    success_url = reverse_lazy('accounts:login')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        #inicializamos el formulario con el usuario actual
        form = PasswordChangeForm(user=self.request.user)
        form.fields['old_password'].widget.attrs['placeholder']='Ingrese su contraseña actual'
        form.fields['new_password1'].widget.attrs['placeholder']='Ingrese su nueva contraseña'
        form.fields['new_password2'].widget.attrs['placeholder']='Repita su nueva contraseña'
        return form

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'edit':
                # https://docs.djangoproject.com/en/4.1/topics/auth/default/
                """Como no tenemos customizado el metodo save, tenemos que crear las validaciones desde aqui"""
                form = PasswordChangeForm(user=request.user, data=request.POST)
                if form.is_valid():
                    form.save()
                    #Evita que se cierre la sesion al cambiar la contrasena
                    #Actualiza la sesion con el nuevo usuario
                    update_session_auth_hash(request, form.user)
                else:
                    #Devolvemos con ajax
                    data['error'] = form.errors
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edición de password'
        context['entity'] = 'Password'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context
