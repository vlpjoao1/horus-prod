from crum import get_current_user
from django.db import models
from datetime import datetime

from django.forms import model_to_dict

from config.settings import MEDIA_URL, STATIC_URL
from core.erp.choices import gender_choices
from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    desc = models.CharField(max_length=500, null=True, blank=True, verbose_name='Descripción')

    def __str__(self):
        return 'Nro:{} / Nombre: {}'.format(self.id, self.name)

    def toJSON(self):
        # item = {'id':self.id, 'name':self.name}
        # Con esto convertirmos el resultado en dict, y a model to dict le pasamos la instancia del objeto actual
        item = model_to_dict(self)  # Podemos excluir valores con exclude=['user_creation','user_updated']
        return item

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        # Obtiene el usuario actual con django-CRUM
        user = get_current_user()
        if user is not None:
            # Si es creacion no tiene PK
            if not self.pk:
                self.user_creation = user
            # si es UPDATE
            else:
                self.user_updated = user
        super(Category, self).save()

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        # https://docs.djangoproject.com/en/4.1/ref/models/options/
        """Personalizando permisos
        permissions=[
            #codename               #Label
            ('can_delete_category', 'Can delete Category')
        ]
        """
        ordering = ['id']


class Product(models.Model):
    name = models.CharField(max_length=150, verbose_name='Nombre', unique=True)
    cat = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Categoría')
    image = models.ImageField(upload_to='product/%Y/%m/%d', null=True, blank=True, verbose_name='Imagen')
    stock = models.IntegerField(default=0, verbose_name='Stock')
    pvp = models.DecimalField(default=0.00, max_digits=9, decimal_places=2, verbose_name='Precio')

    def __str__(self):
        return self.name

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        # imagen por defecto si no se ingresó imagen
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        item = model_to_dict(self)
        item['full_name'] = f'{self.name} / {self.cat.name}'
        item['cat'] = self.cat.toJSON()
        item['image'] = self.get_image()
        item['pvp'] = format(self.pvp, '.2f')
        return item

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['id']


class Client(models.Model):
    names = models.CharField(max_length=150, verbose_name='Nombres')
    surnames = models.CharField(max_length=150, verbose_name='Apellidos')
    dni = models.CharField(max_length=10, unique=True, verbose_name='Dni')
    date_birthday = models.DateField(default=datetime.now, verbose_name='Fecha de nacimiento')
    address = models.CharField(max_length=150, null=True, blank=True, verbose_name='Dirección')
    gender = models.CharField(max_length=10, choices=gender_choices, default='male', verbose_name='Sexo')

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.names} {self.surnames} / {self.dni}'

    def toJSON(self):
        item = model_to_dict(self)
        # https: // dustindavis.me / blog / django - tip - get_field_display / Se usa para los choices
        # lo pasamos con ID y su genero para diferenciarlo por su ID
        item['gender'] = {'id': self.gender, 'name': self.get_gender_display()}
        # formateo el date_birthday
        item['date_birthday'] = self.date_birthday.strftime('%Y-%m-%d')
        item['full_name'] = self.get_full_name()
        return item

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['id']


class Sale(models.Model):
    cli = models.ForeignKey(Client, on_delete=models.CASCADE)
    date_joined = models.DateField(default=datetime.now)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    iva = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    def __str__(self):
        return self.cli.names

    def delete(self, using=None, keep_parents=False):
        #DetSale.objects.filter(sale=self)
        for det in self.detsale_set.all():
            #Modificamos la cantidad del stock del producto con la cantidad del detalle
            det.prod.stock += det.cant
            det.prod.save()
        super(Sale, self).delete()

    def toJSON(self):
        item = model_to_dict(self)
        item['cli'] = self.cli.toJSON()
        item['subtotal'] = format(self.subtotal, '.2f')
        item['iva'] = format(self.iva, '.2f')
        item['total'] = format(self.total, '.2f')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        """
        _set obtiene la relacion inversa de un modelo.
        Como esta Venta esta asociada a un detalle, pero desde la venta no hay
        una relacion directa a detalle sino de detalle a venta, con _set podemos obtener
        esos detalles asociados a esta venta.
        """
        # Si escribimos self.set deben salirnos todas las relaciones inversas
        item['det'] = [i.toJSON() for i in self.detsale_set.all()]
        # Equivale a esto = DeSale.objects.filter(sale_id=self.id)
        return item

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['id']


class DetSale(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    prod = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    cant = models.IntegerField(default=0)
    subtotal = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)

    def __str__(self):
        return self.prod.name

    def toJSON(self):
        # Excluimos la venta ya que no necsitamos la relacion
        item = model_to_dict(self, exclude=['sale'])
        item['prod'] = self.prod.toJSON()
        # Lo formateamos a float porque el valor decimal por default, da error al convertirse a JSON
        item['price'] = format(self.price, '.2f')
        item['subtotal'] = format(self.subtotal, '.2f')
        return item

    class Meta:
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalle de Ventas'
        ordering = ['id']


"""
class Type(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tipo'
        verbose_name_plural = 'Tipos'

        # Como queremos que se llame la tabla
        db_table = 'tipo_emp'
        # como se va a ordenar al hacer un listado
        # Descentende -<campo> ej: ['-id']
        ordering = ['id']


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Nombre')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        db_table = 'categoria_emp'
        ordering = ['id']


class Employees(models.Model):
    # verbose_name, Cuando mapee este clase a modo de formulario el atributo <Label> se mostrará con el valor de este atributo
    dni = models.CharField(max_length=10, unique=True, verbose_name='DNI', null=True)
    date_joined = models.DateField(default=datetime.now, verbose_name='Fecha de registro', null=True)
    # Auto_now= Al crear el registro, se agrará la fecha actual
    date_created = models.DateTimeField(auto_now=True)
    # Auto_now_add= Cada vez que la entidad se actualice se cambia
    date_updated = models.DateTimeField(auto_now_add=True)
    age = models.PositiveIntegerField(default=0)
    salary = models.DecimalField(default=0.00, max_digits=9, decimal_places=2)
    state = models.BooleanField(default=True)
    # Para guardarlo por fechas
    avatar = models.ImageField(upload_to='avatar/%Y/%m', null=True)
    cvitae = models.FileField(upload_to='cvitae/%Y/%m', null=True)
    type = models.ForeignKey(Type, on_delete=models.SET_NULL, null=True)
    categ = models.ManyToManyField(Category)

    # Esto será la representación del objeto cuando lo llames y muestres. Lo mostrará como un STR
    def __str__(self):
        return self.dni

    class Meta:
        # Para cuando registres el modelo en el admin de django
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

        # Como queremos que se llame la tabla
        db_table = 'empleado'
        # como se va a ordenar al hacer un listado
        # Descentende -<campo> ej: ['-id']
        ordering = ['id']
"""
