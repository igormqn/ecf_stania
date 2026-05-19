from django import forms
from django.contrib.auth import get_user_model
from .models import Team, Player, Match

User = get_user_model()


class SignUpForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
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
        label='Amount (€)', required=True
    )
    team_choice = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        label='Chosen team', required=True
    )

    def __init__(self, match=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if match:
            self.fields['team_choice'].queryset = Team.objects.filter(
                pk__in=[match.team1.pk, match.team2.pk]
            )


class PasswordResetForm(forms.Form):
    last_name = forms.CharField(max_length=150, label='Last name')
    email = forms.EmailField(label='Email')

    def clean(self):
        cleaned_data = super().clean()
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        if not User.objects.filter(last_name=last_name, email=email).exists():
            raise forms.ValidationError("No account found with these details.")
        return cleaned_data


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'city']
        labels = {'name': 'Team name', 'city': 'City / Country'}


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'number', 'position', 'team']
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'number': 'Number',
            'position': 'Position',
            'team': 'Team',
        }


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['team1', 'team2', 'game_date', 'start_time', 'end_time', 'odds_team1', 'odds_team2', 'weather']
        labels = {
            'team1': 'Team 1',
            'team2': 'Team 2',
            'game_date': 'Match date',
            'start_time': 'Start time',
            'end_time': 'End time',
            'odds_team1': 'Team 1 odds',
            'odds_team2': 'Team 2 odds',
            'weather': 'Weather',
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
            raise forms.ValidationError("Both teams must be different.")
        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        if start and end and start >= end:
            raise forms.ValidationError("End time must be after start time.")
        return cleaned_data


class CommentaryForm(forms.Form):
    commentary = forms.CharField(
        label='Commentary', widget=forms.Textarea(attrs={'rows': 3}), required=True
    )
    score_team1 = forms.IntegerField(label='Team 1 score', min_value=0, required=False)
    score_team2 = forms.IntegerField(label='Team 2 score', min_value=0, required=False)
