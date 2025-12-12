# apps/groupApp/forms.py
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from apps.userApp.models import AppGroup, User
VERIFIED_FROM_EMAIL = "asma.benhamouda@esprit.tn"  # Must match SendGrid verified sender


class GroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        label="Membres à inviter"
    )

    class Meta:
        model = AppGroup
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Épargne voyage, Famille, Projet maison',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Décrivez l’objectif ou les règles du groupe (facultatif)',
                'rows': 3
            })
        }
        labels = {
            'name': 'Nom du groupe',
            'description': 'Description'
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Exclude current user from member selection
        self.fields['members'].queryset = User.objects.exclude(id=self.user.id)

    def save(self, commit=True):
        group = super().save(commit=False)
        group.created_by = self.user
        if commit:
            group.save()
            added_members = []

            # Add selected members
            for member in self.cleaned_data.get('members', []):
                _, created = group.groupmembre_set.get_or_create(user=member)
                if created:
                    added_members.append(member)

            # Add creator as member
            group.groupmembre_set.get_or_create(user=self.user)

            # 🔔 SEND EMAIL NOTIFICATIONS
            self._send_email_to_creator(group)
            for member in added_members:
                self._send_email_to_member(group, member)

        return group

    def _send_email_to_creator(self, group):
        """Send email to group creator."""
        subject = f"✅ Groupe '{group.name}' créé avec succès !"
        context = {
            'user_firstname': self.user.firstname,
            'group_name': group.name,
        }
        html_message = render_to_string('emails/group_created.html', context)
        try:
            send_mail(
                subject=subject,
                message='',
                from_email=VERIFIED_FROM_EMAIL,
                recipient_list=[self.user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don’t block group creation
            print(f"[EMAIL ERROR] Failed to send email to creator {self.user.email}: {e}")

    def _send_email_to_member(self, group, member):
        """Send email to invited member."""
        subject = f"🎉 Vous avez été ajouté au groupe '{group.name}'"
        context = {
            'user_firstname': member.firstname,
            'group_name': group.name,
            'creator_name': group.created_by.get_full_name(),
        }
        html_message = render_to_string('emails/group_invited.html', context)
        try:
            send_mail(
                subject=subject,
                message='',
                from_email=VERIFIED_FROM_EMAIL,
                recipient_list=[member.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email to {member.email}: {e}")