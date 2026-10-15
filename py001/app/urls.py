from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.incio, name='inicio'),
    path('registrar/', views.registro_render, name='reg_render'),
    path('auth.sys/', views.login_render, name='login_render'),
    path('admin.auth/', views.admin_render, name='admin_render'),
    path('votar/', views.main_render, name='main_render'),
    path('votar/submeter/', views.submeter_voto, name='submeter_voto'),
    path('resultados/', views.resultados, name='resultados'),
    path('sair/', views.sair, name='sair'),
    path('login/', views.logar, name='logar'),
    path(
        'esqueci-senha/',
        auth_views.PasswordResetView.as_view(
            template_name='esqueci-senha.html',
            email_template_name='password_reset_email.txt',
            subject_template_name='password_reset_subject.txt',
            success_url='/esqueci-senha/enviado/',
        ),
        name='password_reset',
    ),
    path(
        'esqueci-senha/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'redefinir-senha/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='redefinir-senha.html',
            success_url='/redefinir-senha/concluido/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'redefinir-senha/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]
