from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .services.summary import build_spending_summary
from .services.recommendations import generate_recommendations
from web_project import TemplateLayout

# @login_required
# def recommendations_view(request):
#     days = int(request.GET.get("days", 30))

#     summary = build_spending_summary(request.user, days=days)
#     recommendations = generate_recommendations(summary)
    
#     return render(request, "recommendations.html", {
#         "summary": summary,
#         "recommendations": recommendations,
#     })
@login_required
def recommendations_view(request):
    days = int(request.GET.get("days", 30))

    summary = build_spending_summary(request.user, days=days)
    recommendations = generate_recommendations(summary)

    context = {
        "summary": summary,
        "recommendations": recommendations,
    }

    # ✅ Inject layout_path + common layout vars
    context = TemplateLayout.init(request, context)

    return render(request, "recommendations.html", context)