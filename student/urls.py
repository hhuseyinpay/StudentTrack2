"""student URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import include
from django.urls import path
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from rest_framework.authtoken import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # path('accounts/', include('django.contrib.auth.urls')),

    # path('', include('daily_study.urls')),

    # path('api/login/', views.ObtainAuthToken.as_view(), name="api-login"),
    path('api/daily_study/', include('daily_study.api.urls')),
    path('api/syllabus/', include('syllabus.api.urls')),
    path('api/accounts/', include('accounts.api.urls')),
]

if settings.DEBUG:
    urlpatterns += [url(r'^silk/', include('silk.urls', namespace='silk'))]
