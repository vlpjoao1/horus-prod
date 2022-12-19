from config.wsgi import *
from django.template.loader import get_template
from weasyprint import HTML, CSS
from config import settings


def printTicket():
    # Obtenemos el template
    template = get_template('ticket.html')
    context = {'name': 'Joao'}
    # Le pasamos datos a ese template
    html_template = template.render(context)
    # Con html crearemos la instancia del archivo y lo pasamos a pdf con lafuncion

    css_url = os.path.join(settings.BASE_DIR,
                           'static/lib/bootstrap-4.4.1-dist/css/bootstrap.min.css')  # Unimos directorio base con static

    #pasamos el css con CSS no como una ruta, sino como una interpretacion que la misma libreria lo pueda usar
    HTML(string=html_template).write_pdf(target='ticket.pdf', stylesheets=[CSS(css_url)])  # target nos permite ponerle nombre


printTicket()
