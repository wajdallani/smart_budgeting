# apps/authentication/urls.py
from django.urls import path
from .views import (
    LoginView, 
    RegisterView, 
    LogoutView, 
    AdminLoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    ResendVerificationCodeView,
    VerifyEmailView
)

urlpatterns = [
    # Inscription
    path("auth/register/", RegisterView.as_view(), name="auth-register-basic"),
    
    # Vérification email
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('resend-code/', ResendVerificationCodeView.as_view(), name='resend-verification-code'),
    
    # Connexion / Déconnexion
    path("auth/login/", LoginView.as_view(), name="auth-login-basic"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    
    # 🔹 Password Reset avec vérification d'email
    path('auth/forgot-password/', 
         PasswordResetView.as_view(), 
         name='auth-forgot-password-basic'),
    
    path('auth/password-reset/done/', 
         PasswordResetDoneView.as_view(), 
         name='password_reset_done'),
    
    path('auth/reset/<uidb64>/<token>/', 
         PasswordResetConfirmView.as_view(), 
         name='password_reset_confirm'),
    
    path('auth/reset/done/', 
         PasswordResetCompleteView.as_view(), 
         name='password_reset_complete'),
]