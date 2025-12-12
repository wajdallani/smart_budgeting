from datetime import date, timedelta
from apps.notificationApp.views import create_debt_reminder
from apps.detteApp.models import Debt  # adjust to your actual model

def send_due_date_notifications():
    today = date.today()
    target_date = today + timedelta(days=2)  # 2 days before due date

    # Filter debts due in exactly 2 days
    debts = Debt.objects.filter(due_date=target_date)

    for debt in debts:
        user = debt.user
        create_debt_reminder(
            user=user,
            debt=debt,
            amount_left=debt.amount_left if hasattr(debt, "amount_left") else None,
            due_date=debt.due_date,
        )
