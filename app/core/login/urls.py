
from django.urls import path

from core.login.views import *

urlpatterns = [
    path('', LoginFormView.as_view(), name='login'),
    #from django
    path('logout/', LogoutView.as_view(next_page='accounts:login'), name='logout'),
    #path('logout2/', LogoutRedirectView.as_view(), name='logout'),
    path('reset/password/', ResetPasswordView.as_view(), name='reset_password'),
    path('change/password/<str:token>/', ChangePasswordView.as_view(), name='change_password'),
]
"""Por lo general, en un update, se pasa el id como argumento, en el caso de datos sensibles,
no sería conveniente pasar el id de ese registro ya que cualquiera podrá modificarlo. Pära eso
podemos usar https://docs.djangoproject.com/en/4.1/ref/models/fields/#uuidfield """