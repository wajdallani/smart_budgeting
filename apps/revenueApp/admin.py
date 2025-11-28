from django.contrib import admin
from .models import Revenue

@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'date', 'user', 'created_at']
    list_filter = ['category', 'date']
    search_fields = ['description', 'category']
