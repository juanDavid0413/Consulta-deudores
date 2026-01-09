from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from .forms import LoginForm, UserCreateForm
from django.contrib.auth.models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user:
            login(request, user)
            # --- ACTIVA LA ANIMACIÓN AQUÍ ---
            request.session['show_welcome_anim'] = True 
            return redirect('dashboard')
        else:
            form.add_error(None, "Usuario o contraseña incorrectos.")

    return render(request, 'accounts/login.html', {'form': form})

# Puedes borrar la función 'custom_login_view' si no la usas en tus URLs

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    # 1. Verificamos si la marca existe en la sesión
    show_anim = request.session.get('show_welcome_anim', False)
    
    # 2. Si existe, la borramos INMEDIATAMENTE de la sesión del servidor
    if show_anim:
        del request.session['show_welcome_anim']
        request.session.modified = True  # Asegura que Django guarde el cambio

    context = {
        "show_welcome_anim": show_anim, # Pasamos la variable al contexto
        "has_any_permission": (
            request.user.has_perm("auth.add_user")
            or request.user.has_perm("accounts.can_upload_excel")
            or request.user.has_perm("auth.can_consult_debtors")
        )
    }
    return render(request, "accounts/dashboard.html", context)

@login_required
@permission_required('auth.add_user', raise_exception=True)
def create_user(request):
    form = UserCreateForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('dashboard')

    return render(request, 'accounts/create_user.html', {'form': form})


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

