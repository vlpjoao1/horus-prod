from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from core.erp.forms import CategoryForm
from core.erp.mixins import IsSuperuserMixin, ValidatePermissionRequiredMixin
from core.erp.models import Category


def category_list(request):
    data = {
        'title': 'Listado de Categorías',
        'categories': Category.objects.all()
    }
    return render(request, 'category/list.html', data)


class CategoryList(ValidatePermissionRequiredMixin, ListView):
    permission_required = 'view_category'
    model = Category
    template_name = 'category/list.html'

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
                contador = 1
                for i in Category.objects.all():
                    item = i.toJSON()
                    item['position']=contador
                    data.append(item)
                    contador += 1
            else:
                data['error'] = 'Ha ocurrido un error'

            # data = Category.objects.get(pk=request.POST['id']).toJson()
        except Exception as e:
            data['error'] = str(e)
        # Para serializar los elementos que no sean diccionaros, debes establecer safe=False
        # Ya que estamos enviando una lista de diccionarios, no un diccionario solo
        return JsonResponse(data, safe=False)

    # Se puede listar solo con modelo y template_name. Hace automaticamente un objects.all
    # Puedes enviar la consulta desde aquí o usar el get_queryset()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de categorías'
        context['create_url'] = reverse_lazy('erp:category_createview')
        context['entity'] = 'Categorías'
        context['list_url'] = reverse_lazy('erp:category_listview')
        return context


"""
    Estas vistas se pueden usar solamente poniendo el modelo, el formulario y el template.
    Sobreescribir los métodos, ya es más para personalización.
"""


class CategoryCreateView(ValidatePermissionRequiredMixin, CreateView):
    permission_required = 'add_category'
    model = Category
    form_class = CategoryForm
    template_name = 'category/create.html'
    # Reverse_lazy devuelve la cadena de texto de esa url
    success_url = reverse_lazy('erp:category_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear una categoría'
        context['entity'] = 'Categorías'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

    def post(self, request, *kargs, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.form_class(request.POST)
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


class CategoryUpdateView(ValidatePermissionRequiredMixin, UpdateView):
    permission_required = 'change_category'
    model = Category
    form_class = CategoryForm
    template_name = 'category/create.html'
    success_url = reverse_lazy('erp:category_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
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
        context['title'] = 'Edición de una Categoria'
        context['entity'] = 'Categorias'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class CategoryDeleteView(ValidatePermissionRequiredMixin, DeleteView):
    permission_required = 'delete_category'
    model = Category
    template_name = 'category/delete.html'
    success_url = reverse_lazy('erp:category_listview')
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
        context['title'] = 'Eliminación de una Categoria'
        context['entity'] = 'Categorias'
        context['list_url'] = self.success_url
        context['action'] = 'delete'
        return context


"""Para que formview guarde/edite/eliminte datos debes sobreescribir los métodos,
    sin sobreescribir, el solo hará las validaciones correspondientes del formulario.
"""


class CategoryFormView(FormView):
    form_class = CategoryForm
    template_name = 'category/create.html'
    success_url = reverse_lazy('erp:category_listview')

    # Aqui se manejan los errores del formulario
    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        print(form.is_valid())
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Form categoría'
        context['entity'] = 'Categorías'
        context['list_url'] = reverse_lazy('erp:category_listview')
        context['action'] = 'add'
        return context
