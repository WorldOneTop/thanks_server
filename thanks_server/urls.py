"""thanks_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from thanks import views

urlpatterns = [
    path('', views.index),
    path('createUser/', views.createUser),
    path('create5Thanks/', views.create5Thanks),
    path('create1Kind/', views.create1Kind),
    path('create1Book/', views.create1Book),
    path('create1Save/', views.create1Save),
    path('createContest/', views.createContest),
    path('updateDocument/', views.updateDocument),
    path('deleteDocument/', views.deleteDocument),
    path('selectDocument/', views.selectDocument),
    path('writeChat/', views.writeChat),
    path('selectChat/', views.selectChat),
    path('createSignup/', views.createSignup),
    path('admin/', admin.site.urls),
]
