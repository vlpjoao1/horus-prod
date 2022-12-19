from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, View
import json

from weasyprint import HTML, CSS

from core.erp.forms import SaleForm, ClientForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Sale, Product, DetSale, Client

# xhtmlpdf
import os
from django.conf import settings
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders


class SaleListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = Sale
    template_name = 'sale/list.html'
    permission_required = 'view_sale'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Sale.objects.all():
                    data.append(i.toJSON())
            # Consultamos los productos de esa venta
            elif action == 'search_details_prod':
                data = []
                for i in DetSale.objects.filter(sale_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['create_url'] = reverse_lazy('erp:sale_createview')
        context['list_url'] = reverse_lazy('erp:sale_listview')
        context['entity'] = 'Ventas'
        return context


class SaleCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    permission_required = 'add_sale'
    model = Sale
    form_class = SaleForm
    template_name = 'sale/create.html'
    # Reverse_lazy devuelve la cadena de texto de esa url
    success_url = reverse_lazy('erp:sale_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Crear una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        # Ya que en el updateview creamos esa variable, aqui la mandamos vacia
        context['det'] = []
        # le mandamos el formulario de cliente al modal
        context['formClient'] = ClientForm
        return context

    def post(self, request, *kargs, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                """Ya que el parametro viene como un JSON, es decir un string, debemos usar json.loads para convertirlo
                a su tipo correcto, en este caso convierte este STR en una LISTA"""
                ids_exlude = json.loads(request.POST['ids'])  # convertirmos el STR en un listado
                # Recibimos TERM de la funcion del autocomplete en la variable DATA del AJAX
                term = request.POST['term'].strip()  # quita caracteres, por default quita espacios

                # obtenemos todos los productos
                products = Product.objects.filter(stock__gt=0)  # mayor que
                # si llega a tener un texto, ahora si lo va a filtrar
                if len(term):
                    products = products.filter(name__icontains=term)
                for i in products.exclude(id__in=ids_exlude)[0:10]:  # excluimos los ids que vienen del template
                    item = i.toJSON()  # retornamos el item
                    # Debemos devolver un dict por cada valor porque asi lo maneja el AUTOCOMPLETE en el SELECT
                    item['value'] = i.name  # retornamos el nombre del item
                    # Usamos text para SELECT y value para autocomplete
                    # item['text'] = i.name  # retornamos el nombre del item
                    data.append(item)
            elif action == 'search_products_select2':
                data = []
                # Recibimos TERM de la funcion del autocomplete en la variable DATA del AJAX
                term = request.POST['term']
                ids_exlude = json.loads(request.POST['ids'])
                """Esto nos servira para mantener escrito el texto en el formulario de select"""
                data.append({'id': term, 'text': term})  # pasamos un id porque siempre requiere un id
                # obtenemos todos los productos
                products = Product.objects.filter()
                # si llega a tener un texto, ahora si lo va a filtrar
                if len(term):
                    products = products.filter(name__icontains=term, stock__gt=0)
                for i in products.exclude(id__in=ids_exlude)[0:10]:
                    item = i.toJSON()  # retornamos el item
                    item['text'] = i.name  # retornamos el nombre del item
                    data.append(item)
            elif action == 'search_clients':
                data = []
                # Recibimos TERM de la funcion del autocomplete en la variable DATA del AJAX
                term = request.POST['term']
                # asi se hace un OR en las consultas Django
                clients = Client.objects.filter(
                    Q(names__icontains=term) | Q(surnames__icontains=term) | Q(dni__icontains=term))[0:10]
                for i in clients:
                    item = i.toJSON()  # retornamos el item (con su id)
                    item['text'] = i.get_full_name()  # retornamos el nombre del item
                    # Debemos devolver un dict po r cada valor porque asi lo maneja el autocomplete en el SELECT
                    # item['value'] = i.names  # retornamos el nombre del item // value es para autocomplete
                    # Usamos text para select2 y value para autocomplete
                    data.append(item)
            elif action == 'add':
                """
                    Al recibir los datos, estamos enviando un dict, pero ese dict se convierte en un str, por eso debemos convertirlo en un dict de vuelta
                """
                with transaction.atomic():  # Revertimos las creaciones si hay algun error en el lote de creacion
                    vents = json.loads(request.POST['vents'])
                    sale = Sale()
                    sale.date_joined = vents['date_joined']
                    # Cuando hacemos referncia a una FK ponemos _id para la relacion (por convencion)
                    sale.cli_id = vents['cli']
                    sale.subtotal = float(vents['subtotal'])
                    sale.iva = float(vents['iva'])
                    sale.total = float(vents['total'])
                    sale.save()
                    # Registramos los productos, asociamos la venta
                    for i in vents['products']:
                        det = DetSale()
                        det.sale_id = sale.id
                        det.prod_id = i['id']
                        det.cant = int(i['cant'])
                        # precio de venta
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()

                        # Podemos acceder a la relacion de esta forma o Product.objects.get(pk=det.prod_id)
                        det.prod.stock -= det.cant
                        det.prod.save()
                    # Enviamos el ID en el response para manejarlo en el ajax y poder generar la factura
                    data = {'id': sale.id}
            elif action == 'create_client':
                with transaction.atomic():
                    # podemos guardarlo de esta forma y asi contamos con las validaciones del FORM
                    formClient = ClientForm(request.POST)
                    """los erroes se retornan como un diccionario, por lo que podemos capturar los errores aqui"""
                    data = formClient.save()
            else:
                data['error'] = 'No ha ingresado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        # Para que se serialize cuando sea una serie de elementos.
        return JsonResponse(data, safe=False)

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


class SaleUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    permission_required = 'change_sale'
    model = Sale
    form_class = SaleForm
    template_name = 'sale/create.html'
    # Reverse_lazy devuelve la cadena de texto de esa url
    success_url = reverse_lazy('erp:sale_listview')
    url_redirect = success_url

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """Ya que esto es un editar, debemos pasarle la instancia al formulario"""
        instance = self.get_object()
        form = SaleForm(instance=instance)
        """ Modificamos el queryset del select y le pasamos el cliente, ya que en el formulario, pusimos que
         su queryset seria vacio. Le pasamos un Filter porque el queryset necesita un listado, si hacemos GET nos 
         daria error"""
        form.fields['cli'].queryset = Client.objects.filter(id=instance.cli.id)
        return form

    def post(self, request, *kargs, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data = []
                """Ya que el parametro viene como un JSON, es decir un string, debemos usar json.loads para convertirlo
                a su tipo correcto, en este caso convierte este STR en una LISTA"""
                ids_exlude = json.loads(request.POST['ids'])  # convertirmos el STR en un listado
                # Recibimos TERM de la funcion del autocomplete en la variable DATA del AJAX
                term = request.POST['term'].strip()  # quita caracteres, por default quita espacios

                # obtenemos todos los productos
                products = Product.objects.filter(stock__gt=0)  # mayor que
                # si llega a tener un texto, ahora si lo va a filtrar
                if len(term):
                    products = products.filter(name__icontains=term)
                for i in products.exclude(id__in=ids_exlude)[0:10]:  # excluimos los ids que vienen del template
                    item = i.toJSON()  # retornamos el item
                    # Debemos devolver un dict por cada valor porque asi lo maneja el AUTOCOMPLETE en el SELECT
                    item['value'] = i.name  # retornamos el nombre del item
                    # Usamos text para SELECT y value para autocomplete
                    # item['text'] = i.name  # retornamos el nombre del item
                    data.append(item)
            elif action == 'search_products_select2':
                data = []
                # Recibimos TERM de la funcion del autocomplete en la variable DATA del AJAX
                term = request.POST['term']
                ids_exlude = json.loads(request.POST['ids'])
                """Esto nos servira para mantener escrito el texto en el formulario de select"""
                data.append({'id': term, 'text': term})  # pasamos un id porque siempre requiere un id
                # obtenemos todos los productos
                products = Product.objects.filter()
                # si llega a tener un texto, ahora si lo va a filtrar
                if len(term):
                    products = products.filter(name__icontains=term, stock__gt=0)
                for i in products.exclude(id__in=ids_exlude)[0:10]:
                    item = i.toJSON()  # retornamos el item
                    item['text'] = i.name  # retornamos el nombre del item
                    data.append(item)
            elif action == 'create_client':
                with transaction.atomic():
                    # podemos guardarlo de esta forma y asi contamos con las validaciones del FORM
                    formClient = ClientForm(request.POST)
                    """los erroes se retornan como un diccionario, por lo que podemos capturar los errores aqui"""
                    data = formClient.save()
            elif action == 'edit':
                """
                    Al recibir los datos, estamos enviando un dict, pero ese dict se convierte en un str, por eso debemos convertirlo en un dict de vuelta
                """
                with transaction.atomic():  # Revertimos las creaciones si hay algun error en el lote de creacion
                    vents = json.loads(request.POST['vents'])
                    # Aqui solo debemos consultar el objeto y lo modificamos
                    # sale = Sale.objects.get(pk=self.get_object().pk)
                    sale = self.get_object()
                    sale.date_joined = vents['date_joined']
                    # Cuando hacemos referncia a una FK ponemos _id para la relacion (por convencion)
                    sale.cli_id = vents['cli']
                    sale.subtotal = float(vents['subtotal'])
                    sale.iva = float(vents['iva'])
                    sale.total = float(vents['total'])
                    sale.save()
                    # Por facilidad eliminamos todos los productos y los volvemos a crear.
                    sale.detsale_set.all().delete()
                    # Registramos los productos, asociamos la venta
                    for i in vents['products']:
                        det = DetSale()
                        det.sale_id = sale.id
                        det.prod_id = i['id']
                        det.cant = int(i['cant'])
                        # precio de venta
                        det.price = float(i['pvp'])
                        det.subtotal = float(i['subtotal'])
                        det.save()
                        # Podemos acceder a la relacion de esta forma o Product.objects.get(pk=det.prod_id)
                        det.prod.stock -= det.cant
                        det.prod.save()
                    data = {'id': sale.id}
            else:
                data['error'] = 'No ha ingresado ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        # Para que se serialize cuando sea una serie de elementos.
        return JsonResponse(data, safe=False)

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

    # lo enviamos dentro del contexto
    def get_details_products(self):
        """
        Debemos enviar el formato necesario para meterlo en la variable products, con su respectiva cantidad, precio etc
        """
        data = []
        try:
            # self.kwargs['pk']
            for i in DetSale.objects.filter(sale_id=self.get_object().id):
                """Ya que producto es una clave foranea, accedemos a el de esta forma"""
                item = i.prod.toJSON()
                item['cant'] = i.cant
                # No enviamos mas datos ya que el calculo del total y todo eso se hace desde js
                data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        """ Ya que obtuvimos una lista de diccionarios, esto va a convertir cada diccionario en un valor de diccionario
        pasara de ser una lista a un diccionario de diccionarios 
        """
        context['det'] = json.dumps(self.get_details_products())  # Lo convertimos a json pq eso necesitamos en JS
        context['formClient'] = ClientForm
        return context


class SaleDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sale/delete.html'
    success_url = reverse_lazy('erp:sale_listview')
    permission_required = 'delete_sale'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        return context

"""Con xhtml2pdf"""
# class SaleInvoicePdfView(LoginRequiredMixin, View):
#     # Esto lo usaremos para trabajar con archivos estaticos
#     def link_callback(self, uri, rel):
#         """
#         Convert HTML URIs to absolute system paths so xhtml2pdf can access those
#         resources
#         """
#         result = finders.find(uri)
#         if result:
#             if not isinstance(result, (list, tuple)):
#                 result = [result]
#             result = list(os.path.realpath(path) for path in result)
#             path = result[0]
#         else:
#             sUrl = settings.STATIC_URL  # Typically /static/
#             sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
#             mUrl = settings.MEDIA_URL  # Typically /media/
#             mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/
#
#             if uri.startswith(mUrl):
#                 path = os.path.join(mRoot, uri.replace(mUrl, ""))
#             elif uri.startswith(sUrl):
#                 path = os.path.join(sRoot, uri.replace(sUrl, ""))
#             else:
#                 return uri
#
#         # make sure that file exists
#         if not os.path.isfile(path):
#             raise Exception(
#                 'media URI must start with %s or %s' % (sUrl, mUrl)
#             )
#         return path
#
#     def get(self, request, *args, **kwargs):
#         # Instanciamos el template con get_template y podremos acceder a los metodos de los datos tipo template
#         template = get_template('sale/invoice.html')
#         context = {
#             'sale': Sale.objects.get(pk=self.kwargs['pk']),
#             'comp': {
#                 'name': 'Joao.INC',
#                 'ruc': '999999999',
#                 'address': 'Carlos Perez'
#             },
#             # debido a que no funcionaba con (settings.STATIC_URL,'img') lo hice asi
#             'icon': '{}{}'.format(settings.BASE_DIR, '/static/img/logo.png')
#         }
#         # Create a Django response object, and specify content_type as pdf
#         response = HttpResponse(content_type='application/pdf')  # Se va a descargar
#         # si no usamos esto no se descarga.
#         # response['Content-Disposition'] = 'attachment; filename="report.pdf"'  # Va a tener este nombre
#         # https://docs.djangoproject.com/en/3.0/topics/templates/
#         # find the template and render it
#         html = template.render(context=context)
#
#         # create a pdf
#         """Pasamos 2 parametros:
#         html: la ruta del objeto que se va a convertir
#         dest: Cual va a ser el objeto que va a contener la conversion"""
#         pisa_status = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)
#         # con linkcalback pasamos la configuracion para los archivos ESTATICOS
#         return response


class SaleInvoicePdfView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # Instanciamos el template con get_template y podremos acceder a los metodos de los datos tipo template
        template = get_template('sale/invoice_weasyprint.html')
        context = {
            'sale': Sale.objects.get(pk=self.kwargs['pk']),
            'comp': {
                'name': 'Joao.INC',
                'ruc': '999999999',
                'address': 'Carlos Perez'
            },
            # debido a que no funcionaba con (settings.STATIC_URL,'img') lo hice asi
            'icon': '{}{}'.format(settings.BASE_DIR, '/static/img/logo.png')
        }
        # response['Content-Disposition'] = 'attachment; filename="report.pdf"'  # Va a tener este nombre
        # https://docs.djangoproject.com/en/3.0/topics/templates/
        # find the template and render it
        html = template.render(context=context)
        css_url = os.path.join(settings.BASE_DIR,
                               'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')  # Unimos directorio base con static

        # pasamos el css con CSS no como una ruta, sino como una interpretacion que la misma libreria lo pueda usar
        pdf = HTML(string=html,
                   base_url=request.build_absolute_uri()).write_pdf(stylesheets=[CSS(css_url)])  # target nos permite ponerle nombre
        """Con build_absolute_Url obtenemos, esto nos servira par las imagenes al momento de cargarlas"""

        # Create a Django response object, and specify content_type as pdf
        # si no usamos esto no se descarga.
        response = HttpResponse(pdf, content_type='application/pdf')  # Se va a descargar

        return response
