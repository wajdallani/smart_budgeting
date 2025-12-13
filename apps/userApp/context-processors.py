# userApp/context_processors.py

from django.db.models import Q

def menu_context(request):
    """
    Context processor pour le menu sidebar et les informations utilisateur
    Accessible dans tous les templates via {{ notifications_count }}, etc.
    """
    context = {
        'notifications_count': 0,
        'user_full_name': '',
    }
    
    # Si l'utilisateur est authentifié
    if request.user.is_authenticated:
        # Nom complet de l'utilisateur
        if hasattr(request.user, 'firstname') and hasattr(request.user, 'lastname'):
            # Si vous utilisez firstname/lastname
            context['user_full_name'] = (
                f"{request.user.firstname} {request.user.lastname}".strip()
            )
        else:
            context['user_full_name'] = (
                f"{request.user.firstname} {request.user.lastname}".strip()
            )
        
        # Si le nom est vide, utiliser l'email
        if not context['user_full_name']:
            context['user_full_name'] = request.user.email
        
        # Compter les notifications non lues (si vous avez un modèle Notification)
        # Décommentez ces lignes si vous avez un modèle Notification
        # try:
        #     from votre_app.models import Notification
        #     context['notifications_count'] = Notification.objects.filter(
        #         user=request.user,
        #         read=False
        #     ).count()
        # except ImportError:
        #     pass
    
    return context