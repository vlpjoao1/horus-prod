"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from core.erp.views.dashboard.views import DashboardView
from core.homepage.views import IndexView
from core.login.views import LoginFormView2, LoginFormView

from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import handler404
from core.erp.views.dashboard.views import page_not_found404

handler404 = page_not_found404

urlpatterns = [
    # path('', IndexView.as_view(), name='index'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('admin/', admin.site.urls),
    path('erp/', include(('core.erp.urls', 'erp'))),
    path('user/', include(('core.user.urls', 'user'))),
    path('login/', include(('core.login.urls', 'accounts'))),
    path('reports/', include(('core.reports.urls', 'reports'))),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
