import os
import sys
import traceback
from pathlib import Path

# Ensure project root is on sys.path so 'config' can be imported
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.utils import timezone
from apps.userApp.models import User
from apps.detteApp.models import Debt, Rappel

try:
    u = User.objects.first()
    print('user id:', u and u.pk)
    d = Debt(title='Automated test debt', original_amount=50, remaining_amount=50, due_date=timezone.now().date(), utilisateur=u)
    d.save()
    print('Debt saved, pk=', d.pk)
    print('Rappels for this debt:', Rappel.objects.filter(debt=d).count())
except Exception:
    traceback.print_exc()
