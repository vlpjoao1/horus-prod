from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.erp.forms import ClientForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Client


class ClientView(ValidatePermissionRequiredMixin,TemplateView):
    permission_required = 'erp.view_client'
    template_name = 'client/list.html'

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
                for i in Client.objects.all():
                    data.append(i.toJSON())
            elif action == 'add':
                """
                    Manejamos los datos con request.POST y no con get_form ya que
                    no estamos trabajando directamente con la vista sinno que estamos
                    abriendo un modal que no pertenece a una vista y estamos pasando el form
                    desde el get_context_data y no como un formulario de la vista
                """
                #recuperamos todos los valores del cliente
                cli = Client()
                cli.names = request.POST['names']
                cli.surnames = request.POST['surnames']
                cli.dni = request.POST['dni']
                cli.date_birthday = request.POST['date_birthday']
                cli.address = request.POST['address']
                cli.gender = request.POST['gender']
                cli.save()
            elif action == 'edit':
                """
                    Manejamos los datos con request.POST y no con get_form ya que
                    no estamos trabajando directamente con la vista sinno que estamos
                    abriendo un modal que no pertenece a una vista y estamos pasando el form
                    desde el get_context_data y no como un formulario de la vista
                """
                #Nuestra instancia sera una consulta, debe ser una consulta
                cli = Client.objects.get(pk=request.POST['id'])
                #recuperamos todos los valores del cliente
                cli.names = request.POST['names']
                cli.surnames = request.POST['surnames']
                cli.dni = request.POST['dni']
                cli.date_birthday = request.POST['date_birthday']
                cli.address = request.POST['address']
                cli.gender = request.POST['gender']
                cli.save()
            elif action == 'delete':
                cli = Client.objects.get(pk=request.POST['id'])
                cli.delete()
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Clientes'
        context['list_url'] = reverse_lazy('erp:client_listview')
        context['entity'] = 'Clientes'
        context['form'] = ClientForm()
        return context