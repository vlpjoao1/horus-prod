from datetime import datetime
from random import randint

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.erp.models import Sale, Product, DetSale


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        #Llamamos el metodo get_group_session para asignarle el grupo al usuario
        request.user.get_group_session()
        #REtornamos denuevo el get para no interrumpir su funcionamiento
        return super().get(request, *args ,**kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'graph_sales_year_month':
                data = self.get_graph_sales_year_month()
                """Podemos hacerlo de esta forma para pasarle el diccionario de una vez al chart
                graphics.addSeries(data);
                """
                # data = {
                #     'name': 'Porcentaje de venta',
                #     'showInLegend': False,
                #     'colorByPoint': True,
                #     'data': self.get_graph_sales_year_month()
                # }
            elif action == 'get_graph_sales_products_year_month':
                data = {
                    'name': 'Porcentaje',
                    'colorByPoint': True,
                    'data': self.get_graph_sales_products_year_month()
                }
            elif action == 'get_graph_online':
                #Le pasamos numeros random para que se maneje con eso
                data = {
                    #aleatorio del 1 al 100
                    'y': randint(1,100)
                }
                print(data)
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    # Con esta variable obtenemos el calculo de cada mes del ano
    def get_graph_sales_year_month(self):
        data = []
        try:
            year = datetime.now().year
            # Iteramos cada mes del ano para calcular las ventas de cada mes
            for m in range(1, 13):
                # Obtenemos la sumatoria total de todas las ventas de cada mes
                total = Sale.objects.filter(date_joined__year=year, date_joined__month=m) \
                    .aggregate(result=Coalesce(Sum('total'), 0)).get('result')
                data.append(float(total))
        except:
            pass
        return data

    def get_graph_sales_products_year_month(self):
        data = []
        year = datetime.now().year
        month = datetime.now().month
        try:
            for p in Product.objects.all():
                """Consultamos el detalle haciendo refencia a la fecha de la venta con sale__, estamos llamando
                a la relacion de la venta."""
                # Obtenemos las ventas de X producto de tal ano de tal mes
                total = DetSale.objects.filter(sale__date_joined__year=year, sale__date_joined__month=month,
                                               prod_id=p.id).aggregate(r=Coalesce(Sum('subtotal'), 0)).get('r')
                """Pasamos la data como la pide la grafica 
                    {name: 'Chrome',y: 70.67,}"""
                if total > 0:
                    data.append({
                        'name': p.name,
                        'y': float(total)
                    })
        except Exception as e:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['panel'] = 'Panel de administrador'
        # context['graph_sales_year_month'] = self.get_graph_sales_year_month()
        return context
