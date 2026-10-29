from django.urls import path
from . import views

urlpatterns = [
    path('', views.incio, name='inicio'),
    path('registrar/', views.registro_render, name='reg_render'),
    path('auth.sys/', views.login_render, name='login_render'),
    path('admin.auth/', views.admin_render, name='admin_render'),
    path('votar/', views.main_render, name='main_render'),
    path('votar/submeter/', views.submeter_voto, name='submeter_voto'),
    path('feedback/enviar/', views.enviar_feedback, name='enviar_feedback'),
    path(
        'feedback/<int:feedback_id>/reagir/',
        views.reagir_feedback,
        name='reagir_feedback',
    ),
    path('resultados/', views.resultados, name='resultados'),
    path('sair/', views.sair, name='sair'),
    path('login/', views.logar, name='logar'),

]
