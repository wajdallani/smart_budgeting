#!/usr/bin/env python
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.detteApp.models import Debt, Rappel
from apps.userApp.models import User
from django.utils import timezone

print("=" * 60)
print("RAPPEL DEBUG INFO")
print("=" * 60)

# Get users
users = User.objects.all()
print(f"\nUsers in DB: {users.count()}")
for u in users:
    print(f"  - {u.pk}: {u.email}")

# Get all debts
debts = Debt.objects.all()
print(f"\nAll Debts: {debts.count()}")
for d in debts:
    print(f"  - pk={d.pk}, title={d.title}, due_date={d.due_date}, user={d.utilisateur_id}")

# Get all rappels
rappels = Rappel.objects.all()
print(f"\nAll Rappels: {rappels.count()}")
for r in rappels:
    print(f"  - pk={r.pk}, debt={r.debt_id}, date_rappel={r.date_rappel}, actif={r.actif}, envoye={r.envoye}")

# Check pending for first user
if users.exists():
    u = users.first()
    print(f"\n--- For user {u.pk} ({u.email}) ---")
    
    now = timezone.now()
    print(f"Current time: {now}")
    
    # Pending rappels for this user
    pending = Rappel.objects.filter(
        debt__utilisateur=u,
        actif=True,
        envoye=False,
        date_rappel__lte=now
    ).order_by('date_rappel')
    
    print(f"Pending rappels (for navbar): {pending.count()}")
    for r in pending:
        print(f"  - pk={r.pk}, debt={r.debt.title}, date_rappel={r.date_rappel}")
    
    # All rappels for this user (regardless of filter)
    all_user_rappels = Rappel.objects.filter(debt__utilisateur=u)
    print(f"All rappels for this user: {all_user_rappels.count()}")
    for r in all_user_rappels:
        print(f"  - pk={r.pk}, debt={r.debt.title}, date_rappel={r.date_rappel}, actif={r.actif}, envoye={r.envoye}")
        print(f"    date_rappel <= now? {r.date_rappel <= now}")

print("\n" + "=" * 60)