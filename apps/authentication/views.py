# apps/authentication/views.py
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.utils.http import url_has_allowed_host_and_scheme

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import RegisterForm, LoginForm


# =============================================================================
# Base Auth View (utilisée par toutes les vues d'authentification)
# =============================================================================
class AuthView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
        })
        return context


# =============================================================================
# Inscription
# =============================================================================
class RegisterView(AuthView):
    template_name = "auth_register_basic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = context.get('form') or RegisterForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('revenue_list')
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Compte créé avec succès ! Bienvenue {user.firstname} !')
            login(request, user)
            return redirect('revenue_list')

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


# =============================================================================
# Connexion classique (utilisateurs normaux)
# =============================================================================
class LoginView(AuthView):
    template_name = "auth_login_basic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = context.get('form') or LoginForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('revenue_list')
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                messages.success(request, f'Bienvenue {user.firstname} !')
                next_url = request.GET.get('next','revenue_list')
                return redirect(next_url)
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


# =============================================================================
# Connexion ADMINISTRATEUR UNIQUEMENT
# =============================================================================
class AdminLoginView(AuthView):
    template_name = "auth/admin_login.html"  # ← ton template spécial admin

    def get(self, request, *args, **kwargs):
        # Déjà connecté en tant qu'admin → dashboard direct
        if request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
            return redirect('admin_dashboard')  # Change avec ton vrai nom d'URL admin

        # Connecté mais pas admin → accès refusé
        if request.user.is_authenticated:
            messages.error(request, "Accès refusé : vous n'êtes pas administrateur.")
            return render(request, self.template_name, {
                'access_denied': True,
                'user': request.user
            })

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('username')        # champ name="username" dans le form
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next', '')

        user = authenticate(request, username=email, password=password)

        # Identifiants corrects ?
        if user and user.is_active:
            # Est-ce un admin ?
            if getattr(user, 'role', None) == 'admin':
                login(request, user)
                messages.success(request, f"Bienvenue dans l'administration, {user.get_full_name()} !")

                redirect_to = next_url or 'admin_dashboard'
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('admin_dashboard')

            else:
                # Bon login, mais PAS admin → REFUS EXPLICITE
                messages.error(request, "Accès refusé : vous n'avez pas les droits d'administrateur.")
                return render(request, self.template_name, {
                    'access_denied': True,
                    'user': user,
                    'email': email
                })
        else:
            # Mauvais identifiants
            messages.error(request, "Identifiants incorrects ou compte désactivé.")
            return render(request, self.template_name, {
                'email': email
            })


# =============================================================================
# Déconnexion
# =============================================================================
class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Vous avez été déconnecté avec succès.')
        return redirect('auth-login-basic')


# =============================================================================
# Mot de passe oublié (optionnel)
# =============================================================================
class ForgotPasswordView(AuthView):
    template_name = "auth_forgot_password_basic.html"