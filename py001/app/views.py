from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .models import e_votos, est, p_votos, pres, s_votos, sec


def incio(_request):
    if _request.user.is_authenticated:
        return redirect('main_render')
    return redirect('login_render')


def login_render(request):
    return render(request, 'login.html')


def logar(request):
    if request.method != 'POST':
        return redirect('login_render')

    email = request.POST.get('email', '').strip()
    senha = request.POST.get('senha', '')
    users = list(User.objects.filter(email__iexact=email)[:2]) if email else []
    user = None
    if len(users) == 1:
        user = authenticate(
            request,
            username=users[0].get_username(),
            password=senha,
        )

    if user is not None:
        login(request, user)
        return redirect('main_render')

    messages.error(request, 'E-mail ou palavra-passe incorretos.')
    return redirect('login_render')


def registro_render(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '')

        if not nome or not email or not senha:
            messages.error(request, 'Preencha todos os campos.')
            return render(request, 'res.html')

        try:
            validate_email(email)
            if User.objects.filter(username=nome).exists():
                raise ValidationError('Este nome de utilizador já está em uso.')
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError('Já existe uma conta com este e-mail.')
            new_user = User(username=nome, email=email)
            validate_password(senha, user=new_user)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)
            return render(request, 'res.html')

        User.objects.create_user(username=nome, email=email, password=senha)
        messages.success(request, 'Conta criada. Já pode iniciar sessão.')
        return redirect('login_render')

    return render(request, 'res.html')


def admin_render(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('resultados')

    if request.method == 'POST':
        username = request.POST.get('user', '').strip()
        password = request.POST.get('chave', '')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('resultados')
        messages.error(request, 'Credenciais administrativas inválidas.')

    return render(request, 'credenciais.html')


@never_cache
@login_required
def main_render(request):
    contexto = {
        'pres': pres.objects.all(),
        'sec': sec.objects.all(),
        'est': est.objects.all(),
        'ja_votou': (
            p_votos.objects.filter(user_id=request.user).exists()
            or s_votos.objects.filter(user_id=request.user).exists()
            or e_votos.objects.filter(user_id=request.user).exists()
        ),
        'nome': request.user.get_full_name() or request.user.get_username(),
    }
    return render(request, 'index.html', contexto)


@login_required
@require_POST
def submeter_voto(request):
    if (
        p_votos.objects.filter(user_id=request.user).exists()
        or s_votos.objects.filter(user_id=request.user).exists()
        or e_votos.objects.filter(user_id=request.user).exists()
    ):
        messages.error(request, 'A sua conta já submeteu um voto.')
        return redirect('main_render')

    presidente = get_object_or_404(pres, pk=request.POST.get('pr'))
    secretaria = get_object_or_404(sec, pk=request.POST.get('sc'))
    estatistico = get_object_or_404(est, pk=request.POST.get('es'))

    try:
        with transaction.atomic():
            p_votos.objects.create(p_id=presidente, user_id=request.user)
            s_votos.objects.create(s_id=secretaria, user_id=request.user)
            e_votos.objects.create(e_id=estatistico, user_id=request.user)
    except IntegrityError:
        messages.error(request, 'A sua conta já submeteu um voto.')
        return redirect('main_render')

    messages.success(request, 'O seu voto foi registado.')
    return redirect('main_render')


@require_POST
def sair(request):
    logout(request)
    messages.success(request, 'Sessão terminada.')
    return redirect('login_render')


@never_cache
@user_passes_test(lambda user: user.is_superuser, login_url='admin_render')
def resultados(request):
    return render(
        request,
        'resultados.html',
        {
            'resultados_por_cargo': (
                ('Presidência', pres.objects.annotate(total_votos=Count('p_votos'))),
                ('Secretariado', sec.objects.annotate(total_votos=Count('s_votos'))),
                ('Estatística', est.objects.annotate(total_votos=Count('e_votos'))),
            ),
            'nome': request.user.get_username(),
        },
    )
