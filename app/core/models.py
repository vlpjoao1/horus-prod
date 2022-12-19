from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    # haciendo referencia al modelo especificado en el settings
    user_creation = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_creation',
                                      null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    """ 
    Como estamos trabajando con relaciones y estamos apuntando a una misma entidad, ocurre un problema con los nombres
    que está asignando django a las FK, por eso debemos especificar el nombre de la relación
    """
    user_updated = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_updated',
                                     null=True, blank=True)
    date_updated = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        #Definimos que este modelo no se va a crear en las tablas, sino que se va a implementar en otras entidades
        abstract = True