from django import forms
from django.contrib.auth import get_user_model
from .models import Team, Player, Match

User = get_user_model()


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email']
        user.username = email
        user.set_password(self.cleaned_data['password1'])
        user.is_active = False
        if commit:
            user.save()
        return user


class BetForm(forms.Form):
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=0,
        label='Montant (€)', required=True
    )
    team_choice = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        label='Équipe choisie', required=True
    )

    def __init__(self, match=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if match:
            self.fields['team_choice'].queryset = Team.objects.filter(
                pk__in=[match.team1.pk, match.team2.pk]
            )


class PasswordResetForm(forms.Form):
    last_name = forms.CharField(max_length=150, label='Nom de famille')
    email = forms.EmailField(label='E-mail')

    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        if not User.objects.filter(last_name=last_name, email=email).exists():
            raise forms.ValidationError("Aucun utilisateur trouvé avec ces informations.")
        return cleaned_data


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'city']
        labels = {'name': 'Nom de l\'équipe', 'city': 'Ville / Pays'}


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'number', 'position', 'team']
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom',
            'number': 'Numéro',
            'position': 'Poste',
            'team': 'Équipe',
        }


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1', 'team2', 'game_date', 'start_time', 'end_time', 'odds_team1', 'odds_team2', 'weather']
        labels = {
            'team1': 'Équipe 1',
            'team2': 'Équipe 2',
            'game_date': 'Date du match',
            'start_time': 'Heure de début',
            'end_time': 'Heure de fin',
            'odds_team1': 'Cote Équipe 1',
            'odds_team2': 'Cote Équipe 2',
            'weather': 'Météo',
        }
        widgets = {
            'game_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'id': 'id_start_time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'id': 'id_end_time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        team1 = cleaned_data.get('team1')
        team2 = cleaned_data.get('team2')
        if team1 and team2 and team1 == team2:
            raise forms.ValidationError("Les deux équipes doivent être différentes.")
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError("L'heure de fin doit être après l'heure de début.")
        return cleaned_data


class CommentaryForm(forms.Form):
    commentary = forms.CharField(
        label='Commentaire', widget=forms.Textarea(attrs={'rows': 3}), required=True
    )
    score_team1 = forms.IntegerField(label='Score Équipe 1', min_value=0, required=False)
    score_team2 = forms.IntegerField(label='Score Équipe 2', min_value=0, required=False)
