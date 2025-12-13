import os
from celery import Celery
from celery.schedules import crontab

# définir la variable d'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('smart_budgeting')

# Charger la configuration depuis settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks dans toutes les apps installées
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


CELERY_BEAT_SCHEDULE = {
    'envoyer-rappels-chaque-heure': {
        'task': 'apps.detteApp.tasks.envoyer_rappels',
        'schedule': crontab(minute=0, hour='*'),  # toutes les heures
    },
}

# Apply beat schedule and timezone to the app configuration
app.conf.beat_schedule = CELERY_BEAT_SCHEDULE
app.conf.timezone = 'UTC'

