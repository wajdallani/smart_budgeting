from django.urls import path
from .views import LoginView, RegisterView, LogoutView, AuthView,AdminLoginView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="auth-login-basic"),
    path("auth/register/", RegisterView.as_view(), name="auth-register-basic"),  # ← RegisterView!
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/forgot_password/", AuthView.as_view(template_name="auth_forgot_password_basic.html"), name="auth-forgot-password-basic"),
    path('admin-login/', AdminLoginView.as_view(), name='admin_login'),
]
