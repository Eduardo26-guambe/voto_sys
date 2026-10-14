from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as LOGIN, logout as LOGOUT
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache as no_cache
from .models import chefe as Chefe, votos as Votos

# função de renderizar pag auth
def auth_fn(request):
    return redirect('auth')

# Função inicial
def inicio(request):
    return render(request, "auth.html", {})

#função de renderizar voto pag
@login_required
@no_cache
def votar_render(request):
    nome= request.user
    
    return render(request, "voto.html", {'uslogado': nome.username})

# função de registro
def registrar_fn(request):

    if request.method=="POST":
        nome=request.POST.get('usname')
        email=request.POST.get('email')
        senha=request.POST.get('senha')

        if User.objects.filter(email=email):
            messages.error(request, 'Email já foi cadastrado, tenta outro')
            return redirect('inicio')
        
        if User.objects.filter(username=nome):
                    messages.error(request, 'Nome de usuário já existe, tente outro')
                    return redirect('inicio')
        
        if len(senha)<4:
            messages.error(request, 'Senha deve ter pelo menos 4 caracteres')
            return redirect('inicio')

        User.objects.create_user(username=nome, email=email, password=senha)
        return redirect('inicio')

    messages.error(request, 'Erro interno, tente novamente')
    return redirect('inicio')

# função de login
def login_fn(request):
    if request.method=="POST":
        nome=request.POST.get('usname')
        senha=request.POST.get('senha')

        user=authenticate(request, username=nome, password=senha)

        if user is not None:
            LOGIN(request, user)
            return redirect('votar_render')
        else:
            messages.error(request, 'Nome de usuário ou senha incorretos')
            return redirect('inicio')

    messages.error(request, 'Erro interno, tente novamente')
    return redirect('inicio')
# função de sair do login
def logout_fn(request):
    LOGOUT(request)
    return redirect('inicio')

# função de votar
def votar_fn(request):
    if request.method == "POST":

        if not request.user.is_authenticated:
            messages.error(request, 'Você precisa estar logado para votar')
            return redirect('inicio')

        

        ##########################################################
        chefe_id=request.POST.get('pr')
        #Buscar o candidato no DB atraves do recebido da pag
        chefe_db=get_object_or_404(Chefe, id=chefe_id)
        usuario_atual= request.user

        #verificar se já votou ou não
        if Votos.objects.filter(user=usuario_atual).exists():
            messages.success(request, 'Já votou nesta eleição!')
            return redirect('votar_render')

        #votar caso o usuario não tenha votado
        Votos.objects.create(chefe=chefe_db, user=usuario_atual)
        messages.success(request, 'Voto registrado com sucesso!')
        return redirect('votar_render')

    messages.error(request, 'Falha ao votar, tente de novo!')
    return redirect('votar_render')