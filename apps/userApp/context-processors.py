from django.db.models import Q
from django.utils import timezone

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
            # Si vous utilisez first_name/last_name (Django par défaut)
            context['user_full_name'] = (
                f"{request.user.first_name} {request.user.last_name}".strip()
            )
        
        # Si le nom est vide, utiliser l'email
        if not context['user_full_name']:
            context['user_full_name'] = request.user.email
        
        # Count pending reminders (Rappel) for this user and expose them
        try:
            from apps.detteApp.models import Rappel

            maintenant = timezone.now()
            pending_rappels = Rappel.objects.filter(
                debt__utilisateur=request.user,
                actif=True,
                envoye=False,
                date_rappel__lte=maintenant
            ).order_by('date_rappel')

            context['notifications_count'] = pending_rappels.count()
            # expose a short list of pending reminders (limit 10)
            context['notifications'] = [
                {
                    'id': r.pk,
                    'message': str(r),
                    'date_rappel': r.date_rappel,
                    'debt_id': r.debt_id,
                }
                for r in pending_rappels[:10]
            ]
        except Exception:
            # If anything fails (import error, DB unavailable), leave defaults
            context['notifications_count'] = context.get('notifications_count', 0)
            context['notifications'] = []
    
    return context