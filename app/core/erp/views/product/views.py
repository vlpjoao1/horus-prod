from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView

from core.erp.forms import ProductForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Product


class ProductList(ValidatePermissionRequiredMixin, ListView):
    permission_required = 'view_product'
    model = Product
    template_name = 'product/list.html'

    # decoradores: Son funciones que añaden funcionalidades a otras funciones.
    # ej: si queremos añadir una validación al metodo dispatch, podemos usar un decorador.

    # dispatch: Es un metodo que se ejecuta al principio de la llamada de una vista. Se encarga de
    # redireccionar a la peticion que se haga, sea post o get.
    # @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Se puede listar solo con modelo y template_name. Hace automaticamente un objects.all
    # Puedes enviar la consulta desde aquí o usar el get_queryset()
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de productos'
        context['create_url'] = reverse_lazy('erp:product_createview')
        context['entity'] = 'Productos'
        context['list_url'] = reverse_lazy('erp:product_listview')
        return context

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Product.objects.all():
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data = {}
            data['error'] = str(e)
        return JsonResponse(data, safe=False)


"""
    Estas vistas se pueden usar solamente poniendo el modelo, el formulario y el template.
    Sobreescribir los métodos, ya es más para personalización.
"""


class ProductCreateView(ValidatePermissionRequiredMixin, CreateView):
    permission_required = 'add_product'
    model = Product
    form_class = ProductForm
    template_name = 'product/create.html'
    # Reverse_lazy devuelve la cadena de texto de esa url
    success_url = reverse_lazy('erp:product_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear una producto'
        context['entity'] = 'Categorías'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        return context

    def post(self, request, *kargs, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'add':
                form = self.get_form()
                data = form.save()
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


class ProductUpdateView(ValidatePermissionRequiredMixin, UpdateView):
    permission_required = 'change_product'
    model = Product
    form_class = ProductForm
    template_name = 'product/create.html'
    success_url = reverse_lazy('erp:product_listview')
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
        context['title'] = 'Edición de una Producto'
        context['entity'] = 'Productos'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        return context


class ProductDeleteView(ValidatePermissionRequiredMixin, DeleteView):
    permission_required = 'delete_product'
    model = Product
    template_name = 'product/delete.html'
    success_url = reverse_lazy('erp:product_listview')
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
        context['title'] = 'Eliminación de un Producto'
        context['entity'] = 'Productos'
        context['list_url'] = self.success_url
        context['action'] = 'delete'
        return context


"""Para que formview guarde/edite/eliminte datos debes sobreescribir los métodos,
    sin sobreescribir, el solo hará las validaciones correspondientes del formulario.
"""


class ProductFormView(FormView):
    form_class = ProductForm
    template_name = 'product/create.html'
    success_url = reverse_lazy('erp:product_listview')

    # Aqui se manejan los errores del formulario
    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Form producto'
        context['entity'] = 'Productos'
        context['list_url'] = reverse_lazy('erp:product_listview')
        context['action'] = 'add'
        return context
