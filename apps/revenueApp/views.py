from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Revenue
from django.db.models import Sum

@login_required
def revenue_list(request):
    revenues = Revenue.objects.filter(user=request.user)
    total_revenue = revenues.aggregate(Sum('amount'))['amount__sum']

    # Fix: Handle None case
    if total_revenue is None:
        total_revenue = 0

    context = {
        'revenues': revenues,
        'total_revenue': total_revenue,
    }
    return render(request, 'revenue/revenue_list.html', context)

@login_required
def revenue_create(request):
    if request.method == 'POST':
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date = request.POST.get('date')

        Revenue.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            description=description,
            date=date
        )
        messages.success(request, 'Revenu ajouté avec succès!')
        return redirect('revenue_list')

    return render(request, 'revenue/revenue_form.html')

@login_required
def revenue_update(request, pk):
    revenue = get_object_or_404(Revenue, pk=pk, user=request.user)

    if request.method == 'POST':
        revenue.amount = request.POST.get('amount')
        revenue.category = request.POST.get('category')
        revenue.description = request.POST.get('description')
        revenue.date = request.POST.get('date')
        revenue.save()

        messages.success(request, 'Revenu modifié avec succès!')
        return redirect('revenue_list')

    context = {'revenue': revenue}
    return render(request, 'revenue/revenue_form.html', context)

@login_required
def revenue_delete(request, pk):
    revenue = get_object_or_404(Revenue, pk=pk, user=request.user)

    if request.method == 'POST':
        revenue.delete()
        messages.success(request, 'Revenu supprimé avec succès!')
        return redirect('revenue_list')

    context = {'revenue': revenue}
    return render(request, 'revenue/revenue_confirm_delete.html', context)