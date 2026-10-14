from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name="inicio"),
    path('autenticacao/', views.auth_fn, name="auth"),
    path('votar.page/', views.votar_render, name="votar_render"),
    path('registrar/', views.registrar_fn, name="registrar"),
    path('login/', views.login_fn, name="login"),
    path('logout/', views.logout_fn, name="logout"),
    path('votar/', views.votar_fn, name="votar"),
]