from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from core.erp.models import Sale
from core.reports.forms import ReportForm


class ReportSaleView(TemplateView):
    template_name = 'sale/report.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_report':
                data = []
                # La ventaja de GET es que si no encontramos el valor podemos poner uno por defecto
                start_date = request.POST.get('start_date', '')
                end_date = request.POST.get('end_date', '')
                search = Sale.objects.all()
                if len(start_date) and len(end_date):
                    search = search.filter(date_joined__range=[start_date, end_date])
                """
                    Lo hacemos de esta forma ya que es una forma diferente, mandamos el array de una vez en vez de un 
                    objeto, para probar algo diferente.
                """
                for s in search:
                    data.append([
                        s.id,
                        s.cli.names,
                        s.date_joined.strftime('%Y-%m-%d'),
                        format(s.subtotal, '.2f'),
                        format(s.iva, '.2f'),
                        format(s.total, '.2f')
                    ])
                # Este ultimo valor sera para la sumatoria total de todos los subtotales
                # https://docs.djangoproject.com/en/3.0/topics/db/aggregation/
                """
                    - Coalesce lo que hace es que si no obtiene un valor, pone por defecto otro, En este caso si no
                    obtiene la sumatoria, ponga por defecto 0
                    - Podemos dejar sin el result= y esto igual nos retorna el valor, pero ponemos esa variable para que
                    el valor se retorn con ese nombre y obtenerlo asi con el GET para buscar en el dict
                        sale = Sale.objects.filter().aggregate(Sum('subtotal'))
                        {'subtotal__sum': Decimal('13719')}
                """
                subtotal = search.aggregate(result=Coalesce(Sum('subtotal'), 0)).get('result')
                iva = search.aggregate(result=Coalesce(Sum('iva'), 0)).get('result')
                total = search.aggregate(result=Coalesce(Sum('total'), 0)).get('result')
                data.append([
                    '----',
                    '----',
                    '----',
                    format(subtotal, '.2f'),
                    format(iva, '.2f'),
                    format(total, '.2f')
                ])
            else:
                data['error'] = 'Ha ocurrido un error'

        except Exception as e:
            data['error'] = str(e)
        # Para serializar los elementos que no sean diccionaros, debes establecer safe=False
        # Ya que estamos enviando una lista de diccionarios, no un diccionario solo
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Reporte de las ventas'
        context['list_url'] = reverse_lazy('reports:sale_reportview')
        context['entity'] = 'Reportes'
        context['form'] = ReportForm()
        return context
