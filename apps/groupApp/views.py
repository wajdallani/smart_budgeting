# apps/groupApp/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.userApp.models import AppGroup, User
from .forms import GroupForm
from web_project import TemplateLayout
from django.core.mail import send_mail
from django.conf import settings

layout = TemplateLayout()

@login_required
def group_list(request):
    groups = AppGroup.objects.filter(groupmembre__user=request.user).distinct()
    context = {'groups': groups}
    context = layout.init(context)
    return render(request, 'groupApp/group_list.html', context)

@login_required
def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()# This should set created_by = request.user inside the form

           
            messages.success(request, "✅ Groupe créé avec succès !")
            return redirect('groupApp:group_list')
    else:
        form = GroupForm(user=request.user)
    
    context = {'form': form, 'titre': 'Créer un groupe'}
    context = layout.init(context)
    return render(request, 'groupApp/group_form.html', context)

@login_required
def group_update(request, pk):
    group = get_object_or_404(AppGroup, pk=pk)
    if request.user != group.created_by and not request.user.is_admin:
        messages.error(request, "⚠️ Seul le créateur ou un admin peut modifier ce groupe.")
        return redirect('groupApp:group_list')
    
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Groupe mis à jour !")
            return redirect('groupApp:group_list')
    else:
        form = GroupForm(instance=group, user=request.user)
    
    context = {'form': form, 'titre': 'Modifier le groupe'}
    context = layout.init(context)
    return render(request, 'groupApp/group_form.html', context)

@login_required
def group_delete(request, pk):
    group = get_object_or_404(AppGroup, pk=pk)
    if request.user != group.created_by and not request.user.is_admin:
        messages.error(request, "⚠️ Seul le créateur ou un admin peut supprimer ce groupe.")
        return redirect('groupApp:group_list')
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f"🗑️ Le groupe '{group_name}' a été supprimé.")
        return redirect('groupApp:group_list')
    
    context = {'group': group}
    context = layout.init(context)
    return render(request, 'groupApp/group_confirm_delete.html', context)