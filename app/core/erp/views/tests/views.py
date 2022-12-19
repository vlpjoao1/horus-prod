from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.erp.forms import TestForm
from core.erp.models import Product, Category


class TestView(TemplateView):
    template_name = 'send_email.html'

    @method_decorator(csrf_exempt)
    #@method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    # Se puede listar solo con modelo y template_name. Hace automaticamente un objects.all
    # Puedes enviar la consulta desde aquí o usar el get_queryset()

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_product_id':
                # Como el formulario no tiene el primer valor vació, tenemos que iniciarlizarlo de una vez
                data = [{'id': '', 'text': '-------'}]
                for i in Product.objects.filter(cat_id=request.POST['id']):
                    data.append({'id': i.id, 'text': i.name})
            elif action == 'autocomplete':
                # data sera un array para devolver un array
                data = []
                # Evitamos mandar todos los registros [0:10] para no sobrecargar el sistema
                for i in Category.objects.filter(name__icontains=request.POST['term'])[0:10]:
                    # Debemos devolver un dict por cada valor porque asi lo maneja el autocomplete
                    item = i.toJSON()
                    item['value'] = i.name
                    data.append(item)
            elif action == 'autocomplete2':
                # data sera un array para devolver un array
                data = []
                # Evitamos mandar todos los registros [0:10] para no sobrecargar el sistema
                for i in Category.objects.filter(name__icontains=request.POST['term'])[0:10]:
                    # Debemos devolver un dict por cada valor porque asi lo maneja el autocomplete
                    item = i.toJSON()#ID
                    """Debe retornar un valor TEXT porque ej SELECT2 se manejan los datos asi
                        {
                          "id": 2,
                          "text": "Option 2"
                        }
                    """
                    item['text'] = i.name #TEXT
                    data.append(item)
                    print(data)
            else:
                data['error'] = 'Ha ocurrido un error'

            # data = Category.objects.get(pk=request.POST['id']).toJson()
        except Exception as e:
            data = {}
            data['error'] = str(e)
        # Para serializar los elementos que no sean diccionaros, debes establecer safe=False
        # Ya que estamos enviando una lista de diccionarios, no un diccionario solo
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tile'] = 'Select aninados | Django'
        context['form'] = TestForm()
        return context
