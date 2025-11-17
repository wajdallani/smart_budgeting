# apps/authentication/views.py
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import RegisterForm, LoginForm


class AuthView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update({
            "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
        })
        return context


class RegisterView(AuthView):
    template_name = "auth_register_basic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = RegisterForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        context = self.get_context_data()
        context['form'] = RegisterForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        context = self.get_context_data()
        
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f'Compte créé avec succès! Bienvenue {user.firstname}!'
            )
            # Connecter automatiquement l'utilisateur après l'inscription
            login(request, user)
            return redirect('index')
        
        context['form'] = form
        return self.render_to_response(context)


class LoginView(AuthView):
    template_name = "auth_login_basic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = LoginForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        context = self.get_context_data()
        context['form'] = LoginForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        context = self.get_context_data()
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)
            
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # Gérer "Se souvenir de moi"
                if not remember_me:
                    request.session.set_expiry(0)
                
                messages.success(
                    request,
                    f'Bienvenue {user.firstname}!'
                )
                
                # Rediriger vers la page demandée ou l'index
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(
                    request,
                    'Email ou mot de passe incorrect.'
                )
        
        context['form'] = form
        return self.render_to_response(context)


class LogoutView(TemplateView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.info(request, 'Vous avez été déconnecté avec succès.')
        return redirect('auth-login-basic')


class ForgotPasswordView(AuthView):
    template_name = "auth_forgot_password_basic.html"