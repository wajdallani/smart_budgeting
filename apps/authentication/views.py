# apps/authentication/views.py
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.utils.http import url_has_allowed_host_and_scheme
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from .forms import RegisterForm, LoginForm, VerificationCodeForm, CustomPasswordResetForm
from config.utils import send_verification_email
from apps.userApp.models import User


# =============================================================================
# Base Auth View
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
# apps/authentication/views.py (partie RegisterView)

class RegisterView(AuthView):
    template_name = "auth_register_basic.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = context.get('form') or RegisterForm()
        return context

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('revenueApp:revenue_list')
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        
        # 🔹 Validation manuelle pour permettre les emails inactifs
        if form.is_valid():
            email = form.cleaned_data['email']
            firstname = form.cleaned_data['firstname']
            lastname = form.cleaned_data['lastname']
            password = form.cleaned_data['password']
            
            # 🔹 Vérifier si un compte inactif existe
            try:
                existing_user = User.objects.get(email=email)
                
                if existing_user.is_active:
                    # Compte actif : refuser
                    form.add_error('email', 'Cette adresse email est déjà utilisée par un compte actif.')
                    context = self.get_context_data()
                    context['form'] = form
                    return self.render_to_response(context)
                else:
                    # Compte inactif : mettre à jour
                    existing_user.firstname = firstname
                    existing_user.lastname = lastname
                    existing_user.set_password(password)
                    existing_user.is_active = False
                    existing_user.is_email_verified = False
                    existing_user.email_verification_code = None
                    existing_user.verification_code_created_at = None
                    existing_user.save()
                    
                    user = existing_user
                    is_reactivation = True
                    
            except User.DoesNotExist:
                # Nouveau compte : créer
                user = User.objects.create_user(
                    email=email,
                    password=password,
                    firstname=firstname,
                    lastname=lastname,
                    role='utilisateur',
                    is_active=False,
                    is_email_verified=False
                )
                is_reactivation = False
            
            # Générer et envoyer le code de vérification
            verification_code = user.generate_verification_code()
            
            if send_verification_email(user, verification_code):
                request.session['pending_user_id'] = user.id
                
                if is_reactivation:
                    messages.success(
                        request, 
                        f'Vos informations ont été mises à jour. '
                        f'Un nouveau code de vérification a été envoyé à {user.email}. '
                        f'Veuillez vérifier votre email pour activer votre compte.'
                    )
                else:
                    messages.success(
                        request, 
                        f'Compte créé avec succès ! Un code de vérification a été envoyé à {user.email}. '
                        f'Veuillez vérifier votre email pour activer votre compte.'
                    )
                
                return redirect('verify-email')
            else:
                messages.error(
                    request,
                    "Erreur lors de l'envoi de l'email. Veuillez réessayer."
                )
                if not is_reactivation:
                    user.delete()

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


# =============================================================================
# Vérification de l'email
# =============================================================================
class VerifyEmailView(AuthView):
    template_name = "auth_verify_email.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = context.get('form') or VerificationCodeForm()
        
        pending_user_id = self.request.session.get('pending_user_id')
        if pending_user_id:
            try:
                user = User.objects.get(id=pending_user_id)
                context['user_email'] = user.email
            except User.DoesNotExist:
                pass
        
        return context

    def get(self, request, *args, **kwargs):
        if 'pending_user_id' not in request.session:
            messages.warning(request, "Aucune vérification en cours.")
            return redirect('auth-register-basic')
        
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = VerificationCodeForm(request.POST)
        pending_user_id = request.session.get('pending_user_id')

        if not pending_user_id:
            messages.error(request, "Session expirée. Veuillez vous réinscrire.")
            return redirect('auth-register-basic')

        try:
            user = User.objects.get(id=pending_user_id)
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
            return redirect('auth-register-basic')

        if form.is_valid():
            code = form.cleaned_data['code']
            
            if user.is_verification_code_valid(code):
                user.verify_email()
                del request.session['pending_user_id']
                login(request, user, backend='apps.authentication.backends.EmailBackend')
                messages.success(request, f'Email vérifié et compte activé avec succès ! Bienvenue {user.firstname} !')
                return redirect('revenueApp:revenue_list')
            else:
                messages.error(request, 'Code invalide ou expiré. Veuillez réessayer.')

        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)


# =============================================================================
# Renvoyer le code de vérification
# =============================================================================
class ResendVerificationCodeView(View):
    def post(self, request, *args, **kwargs):
        pending_user_id = request.session.get('pending_user_id')
        
        if not pending_user_id:
            messages.error(request, "Aucune vérification en cours.")
            return redirect('auth-register-basic')

        try:
            user = User.objects.get(id=pending_user_id)
            verification_code = user.generate_verification_code()
            
            if send_verification_email(user, verification_code):
                messages.success(request, f'Un nouveau code a été envoyé à {user.email}')
            else:
                messages.error(request, "Erreur lors de l'envoi de l'email.")
                
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
            return redirect('auth-register-basic')

        return redirect('verify-email')


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
            return redirect('revenueApp:revenue_list')
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', False)

            try:
                user_check = User.objects.get(email=email)
                
                if not user_check.is_active:
                    verification_code = user_check.generate_verification_code()
                    send_verification_email(user_check, verification_code)
                    request.session['pending_user_id'] = user_check.id
                    
                    messages.error(
                        request,
                        "⚠️ Vous n'avez pas confirmé votre adresse email. Votre compte reste inactif. "
                        "Un nouveau code de vérification a été envoyé à votre adresse email."
                    )
                    return redirect('verify-email')
                
            except User.DoesNotExist:
                pass

            user = authenticate(request, username=email, password=password)

            if user is not None:
                if not user.is_active or not user.is_email_verified:
                    verification_code = user.generate_verification_code()
                    send_verification_email(user, verification_code)
                    request.session['pending_user_id'] = user.id
                    
                    messages.error(
                        request,
                        "⚠️ Vous n'avez pas confirmé votre adresse email. Votre compte reste inactif. "
                        "Un nouveau code de vérification a été envoyé à votre adresse email."
                    )
                    return redirect('verify-email')
                
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)

                messages.success(request, f'Bienvenue {user.firstname} !')
                next_url = request.GET.get('next', 'revenueApp:revenue_list')
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
    template_name = "auth/admin_login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and getattr(request.user, 'role', None) == 'admin':
            return redirect('admin_dashboard')

        if request.user.is_authenticated:
            messages.error(request, "Accès refusé : vous n'êtes pas administrateur.")
            return render(request, self.template_name, {
                'access_denied': True,
                'user': request.user
            })

        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        email = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next', '')

        user = authenticate(request, username=email, password=password)

        if user and user.is_active:
            if getattr(user, 'role', None) == 'admin':
                login(request, user)
                messages.success(request, f"Bienvenue dans l'administration, {user.get_full_name()} !")

                redirect_to = next_url or 'admin_dashboard'
                if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "Accès refusé : vous n'avez pas les droits d'administrateur.")
                return render(request, self.template_name, {
                    'access_denied': True,
                    'user': user,
                    'email': email
                })
        else:
            messages.error(request, "Identifiants incorrects, compte désactivé ou non vérifié.")
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
# Réinitialisation de mot de passe - VERSION PERSONNALISÉE
# =============================================================================
class PasswordResetView(AuthView, auth_views.PasswordResetView):
    """
    Vue personnalisée pour la réinitialisation de mot de passe
    Vérifie si l'email existe avant d'envoyer le lien
    """
    template_name = "auth_forgot_password_basic.html"
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    form_class = CustomPasswordResetForm  # 🔹 Utiliser le formulaire personnalisé
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter un flag pour afficher le bouton d'inscription si l'email n'existe pas
        context['show_register_button'] = False
        return context
    
    def form_invalid(self, form):
        # Si le formulaire est invalide (email n'existe pas)
        context = self.get_context_data(form=form)
        context['show_register_button'] = True
        return self.render_to_response(context)


class PasswordResetDoneView(AuthView, auth_views.PasswordResetDoneView):
    template_name = "password_reset_done.html"


class PasswordResetConfirmView(AuthView, auth_views.PasswordResetConfirmView):
    template_name = "password_reset_confirm.html"
    success_url = reverse_lazy('password_reset_complete')


class PasswordResetCompleteView(AuthView, auth_views.PasswordResetCompleteView):
    template_name = "password_reset_complete.html"