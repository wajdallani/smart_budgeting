from datetime import timedelta
from django.utils import timezone

def build_spending_summary(user, days: int = 30) -> dict:
    start_date = timezone.now().date() - timedelta(days=days)

    from apps.depenseApp.models import Depense

    qs = Depense.objects.filter(user=user, date__gte=start_date)

    total_spent = sum(float(x.amount) for x in qs)

    by_cat = {}
    for e in qs.select_related("categorie"):   # ✅ correct FK name
        cat_name = e.categorie.nom if e.categorie else "Uncategorized"  # ✅ correct field
        by_cat[cat_name] = by_cat.get(cat_name, 0.0) + float(e.amount)

    top_categories = sorted(by_cat.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "period_days": days,
        "start_date": str(start_date),
        "total_spent": round(total_spent, 2),
        "transactions_count": qs.count(),
        "top_categories": [
            {"category": c, "amount": round(a, 2)} for c, a in top_categories
        ],
    }