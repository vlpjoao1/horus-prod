from django.urls import path
from core.erp.views.category.views import category_list, CategoryList, CategoryCreateView, CategoryUpdateView, \
    CategoryDeleteView, CategoryFormView
from core.erp.views.client.views import ClientView
from core.erp.views.dashboard.views import DashboardView
from core.erp.views.product.views import ProductList, ProductCreateView, ProductUpdateView, ProductDeleteView
from core.erp.views.sale.views import SaleCreateView, SaleListView, SaleDeleteView, SaleUpdateView, SaleInvoicePdfView
from core.erp.views.tests.views import TestView

urlpatterns = [
    path('category/list/', CategoryList.as_view(), name='category_listview'),
    path('category/create/', CategoryCreateView.as_view(), name='category_createview'),
    path('category/update/<int:pk>/', CategoryUpdateView.as_view(), name='category_updateview'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='category_deleteview'),
    path('category/form/', CategoryFormView.as_view(), name='category_formview'),
    #product
    path('product/list/', ProductList.as_view(), name='product_listview'),
    path('product/create/', ProductCreateView.as_view(), name='product_createview'),
    path('product/update/<int:pk>/', ProductUpdateView.as_view(), name='product_updateview'),
    path('product/delete/<int:pk>/', ProductDeleteView.as_view(), name='product_deleteview'),
    #Client
    path('client/', ClientView.as_view(), name='client_listview'),
    #Sale
    path('sale/create/', SaleCreateView.as_view(), name='sale_createview'),
    path('sale/list/', SaleListView.as_view(), name='sale_listview'),
    path('sale/delete/<int:pk>/', SaleDeleteView.as_view(), name='sale_deleteview'),
    path('sale/update/<int:pk>/', SaleUpdateView.as_view(), name='sale_updateview'),
    path('sale/invoice/pdf/<int:pk>/', SaleInvoicePdfView.as_view(), name='sale_invoice_pdfview'),
    #dashboard
    #path('dashboard/', DashboardView.as_view(), name='dashboard'),
    #test
    path('test/', TestView.as_view(), name='test'),
]
