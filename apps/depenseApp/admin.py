from django.contrib import admin
from .models import Depense


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('depense_id', 'amount', 'date', 'notes', 'created_at')
    list_filter = ('date', 'created_at')
    search_fields = ('depense_id', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-date', '-created_at')