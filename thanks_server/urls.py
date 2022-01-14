from django.contrib import admin
from django.urls import path
from thanks import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('', views.index),
    path('admin/', views.admin),
    path('login/', views.login),
    path('checkLogin/', views.checkLogin),
    path('signupList/', views.signupList),
    path('createUser/', views.createUser),
    path('create5Thanks/', views.create5Thanks),
    path('create1Doc/', views.create1Doc),
    path('updateDocument/', views.updateDocument),
    path('deleteDocument/', views.deleteDocument),
    path('selectDocument/', views.selectDocument),
    path('writeChat/', views.writeChat),
    path('readChat/', views.readChat),
    path('management/', views.management),
    path('management/appendTerm/', views.appendTerm),
    path('management/updateTerm/', views.updateTerm),
    path('management/manager/', views.manager),
    path('management/managerPw/', views.managerPw),
    path('createSignup/', views.createSignup),
    path('signupList/acceptSignup/', views.acceptSignup),
    path('adminSearch/', views.adminSearch),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
