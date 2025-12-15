from django.urls import path
from .views import recommendations_view
from django.views.generic import RedirectView

app_name = "aiApp"

urlpatterns = [
    path("recommendations/", recommendations_view, name="recommendations"),
]