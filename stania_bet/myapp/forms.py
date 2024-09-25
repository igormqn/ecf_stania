from django import forms
from .models import Team, CustomUser
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django import forms
from django.conf import settings
from django.contrib import messages
from .models import Team, Player, Match
from .forms import PasswordResetForm
import random
import string

class SignUpForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email


class BetForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=True)
    team_choice = forms.ModelChoiceField(queryset=Team.objects.all(), required=True)

class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")
    email = forms.EmailField(label="E-mail")
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        
        if not CustomUser.objects.filter(username=username, email=email).exists():
            raise forms.ValidationError("Aucun utilisateur trouvé avec ces informations.")

def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(username=username, email=email)

            # Générer un nouveau mot de passe aléatoire
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            user.set_password(new_password)
            user.save()

            # Envoyer un e-mail avec le nouveau mot de passe
            subject = 'Votre nouveau mot de passe'
            message = f'Votre nouveau mot de passe est : {new_password}. Vous devrez le changer lors de votre prochaine connexion.'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, "Un e-mail contenant votre nouveau mot de passe a été envoyé.")
            return redirect('signin')
    else:
        form = PasswordResetForm()
    
    return render(request, 'password_reset.html', {'form': form})

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'city']

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['name', 'position', 'team']

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team_home', 'team_away', 'match_date', 'match_time', 'odds_home', 'odds_away']

    def clean(self):
        cleaned_data = super().clean()
        team_home = cleaned_data.get("team_home")
        team_away = cleaned_data.get("team_away")

        if team_home == team_away:
            raise forms.ValidationError("Les équipes ne peuvent pas être identiques.")