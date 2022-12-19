from django.forms import *

from core.user.models import User


class UserForm(ModelForm):
    """
        Usamos el constructor para agregar valores a todo.
        Iteremos los items del formulario para agregarle atributos de forma automatica y no manual.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = User
        # Para que se muestren en orden en pantalla lo defines aca
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'image', 'groups')
        exclude = ['last_login', 'date_joined', 'user_permissions', 'is_staff', 'is_superuser', 'is_active']
        widgets = {
            'first_name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombres',
                    'autocomplete': 'off'
                }
            ),
            'last_name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus apellidos',
                    'autocomplete': 'off'
                }
            ),
            'username': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus usuario',
                    'autocomplete': 'off'
                }
            ),
            'email': TextInput(
                attrs={
                    'placeholder': 'Ingrese su email',
                    'autocomplete': 'off'
                }
            ),
            'password': PasswordInput(
                # PAra que se muestre la contrasena en pantalla
                render_value=True,
                attrs={
                    'placeholder': 'Ingrese su password',
                    'autocomplete': 'off'
                }
            ),
            'groups': SelectMultiple(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%',
                'multiple': 'multiple'
            }),
        }

    """
        Al sobreescribir el metodo save perdemos algunas cosas importantes. Como el guardado de los permisos y los
        grupos de usuarios.
    """

    def save(self, commit=True):
        data = {}
        # con esto, recuperamos el formulario
        # podríamos hacerlo con self tambien
        form = super()
        try:
            if form.is_valid():
                # Contrasena metida en el formulario
                pwd = self.cleaned_data['password']
                # HAce una pausa al guardado y devuelve en una variable el objeto actual
                u = form.save(commit=False)
                if u.pk is None:
                    # se encripta la contrasena
                    u.set_password(pwd)
                else:
                    # Verificamos si la contrasena fue cambiada para saber si encriptarla
                    user = User.objects.get(pk=u.pk)
                    if user.password != pwd:
                        u.set_password(pwd)
                u.save()
                """
                    Cuando quitamos un grupo del formulario, este no se borra de la DB, primero debemos limpiar todos los
                    grupos y luego guardarlos de nuevo
                """
                u.groups.clear()
                # Asi guardamos los grupos, les pasamos la instancia
                for g in self.cleaned_data['groups']:
                    u.groups.add(g)
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data

    # def clean(self):
    #     # obtenemos el objeto
    #     cleaned = super().clean()
    #     if len(cleaned['name']) <= 4:
    #         # Agregar errores a los campos.
    #         self.add_error('name', 'Te faltan caracteres')
    #         """Retornar errores que no son propios de los formularios, es decir, errores generales
    #         Este error se representa con form.non_field_errors (no tienen nada que ver con los fields)
    #         https://docs.djangoproject.com/en/3.0/ref/forms/api/"""
    #         raise forms.ValidationError('Validación XX')
    #     return cleaned


class UserProfileForm(ModelForm):
    """
        Usamos el constructor para agregar valores a todo.
        Iteremos los items del formulario para agregarle atributos de forma automatica y no manual.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['autofocus'] = True

    class Meta:
        model = User
        # Para que se muestren en orden en pantalla lo defines aca
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'image')
        exclude = ['last_login', 'date_joined', 'user_permissions', 'is_staff', 'is_superuser', 'is_active', 'groups']
        widgets = {
            'first_name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus nombres',
                    'autocomplete': 'off'
                }
            ),
            'last_name': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus apellidos',
                    'autocomplete': 'off'
                }
            ),
            'username': TextInput(
                attrs={
                    'placeholder': 'Ingrese sus usuario',
                    'autocomplete': 'off'
                }
            ),
            'email': TextInput(
                attrs={
                    'placeholder': 'Ingrese su email',
                    'autocomplete': 'off'
                }
            ),
            'password': PasswordInput(
                # PAra que se muestre la contrasena en pantalla
                render_value=True,
                attrs={
                    'placeholder': 'Ingrese su password',
                    'autocomplete': 'off'
                }
            )
        }

    """
        Al sobreescribir el metodo save perdemos algunas cosas importantes. Como el guardado de los permisos y los
        grupos de usuarios.
    """

    def save(self, commit=True):
        data = {}
        # con esto, recuperamos el formulario
        # podríamos hacerlo con self tambien
        form = super()
        try:
            if form.is_valid():
                # Contrasena metida en el formulario
                pwd = self.cleaned_data['password']
                # HAce una pausa al guardado y devuelve en una variable el objeto actual
                u = form.save(commit=False)
                if u.pk is None:
                    # se encripta la contrasena
                    u.set_password(pwd)
                else:
                    # Verificamos si la contrasena fue cambiada para saber si encriptarla
                    user = User.objects.get(pk=u.pk)
                    if user.password != pwd:
                        u.set_password(pwd)
                u.save()
            else:
                data['error'] = form.errors
        except Exception as e:
            data['error'] = str(e)
        return data
