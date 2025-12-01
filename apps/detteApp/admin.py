from django.contrib import admin
from .models import Debt, Payment
# Register your models here.

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('title', 'creditor', 'debtor', 'remaining_amount', 'due_date')
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('debt', 'amount', 'date', 'created_at')