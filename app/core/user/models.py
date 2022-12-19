import uuid

from crum import get_current_request
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.db import models

# Create your models here.

# Debido a que AbstractUser contiene ya varios campos creados, no necesitamos renombrar campos.
from django.forms import model_to_dict

from config.settings import MEDIA_URL, STATIC_URL


class User(AbstractUser):
    image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)
    """ #Este token se usará para los cambios de contraseña, par no pasar el id como argumento.
    Este token se generará en la vista al momento de enviar el correo."""
    token = models.UUIDField(primary_key=False, null=True, blank=True, editable=False)

    def get_image(self):
        if self.image:
            return '{}{}'.format(MEDIA_URL, self.image)
        # imagen por defecto si no se ingresó imagen
        return '{}{}'.format(STATIC_URL, 'img/empty.png')

    def toJSON(self):
        """Model_to_dict tiene limitantes, algunos campos no se pueden convertir a dict como FECHAS, IMAGENES, Relaciones
        Para eso podemos usar metodos como exclude para poder excluir esos campos limitantes"""
        item = model_to_dict(self,
                             exclude=['password', 'user_permissions', 'last_login'])
        """ Lo convertimos a algo manejable, ya que del model_to_dict 
         viene asi ('date_joined': datetime.datetime(2022, 11, 3, 19, 2, 13, 124805, tzinfo=<UTC>))"""
        if self.last_login:
            item['last_login'] = self.last_login.strftime('%Y-%m-%d')
        item['date_joined'] = self.date_joined.strftime('%Y-%m-%d')
        item['image'] = self.get_image()
        #Este es un metodo propio de abstractuser
        item['full_name'] = self.get_full_name()
        item['groups'] = [{'id':g.id,'name':g.name} for g in self.groups.all()]
        return item

    """Podemos sobreescribir los metodos de los modelos para que se ejecuten cada vez 
        que se realice una accion con el modelo
    """

    def get_group_session(self):
        #Django crum
        #obtenemos la sesion actual
        request = get_current_request()
        #CONSULTAMOS LOS GRUPOS DEL USER actual
        groups = self.groups.all()
        if groups.exists():
            # Si no esta la variable grupo en la sesion, le asignara un grupo a la sesion
            if 'group' not in request.session:
                #Le asigna el primer grupo del usuario a la sesion
                request.session['group'] = groups[0]


    # def save(self, *args, **kwargs):
    #     # si es un nuevo registro
    #     if self.pk is None:
    #         # se encripta la contrasena
    #         self.set_password(self.password)
    #     else:
    #         #Verificamos si la contrasena fue cambiada para saber si encriptarla
    #         user = User.objects.get(pk=self.pk)
    #         if user.password != self.password:
    #             self.set_password(self.password)
    #     super().save(*args, **kwargs)
