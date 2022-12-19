from django.contrib import admin
from core.erp.models import Category, Product, Client
# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Client)