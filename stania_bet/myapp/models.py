from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default='Unknown')

    class Meta:
        unique_together = ('name', 'city')
        ordering = ['name']

    def __str__(self):
        return f"{self.city} {self.name}"


class Player(models.Model):
    POSITION_CHOICES = [
        ('QB', 'Quarterback'),
        ('RB', 'Running Back'),
        ('FB', 'Fullback'),
        ('WR', 'Wide Receiver'),
        ('TE', 'Tight End'),
        ('G', 'Guard'),
        ('T', 'Tackle'),
        ('C', 'Center'),
        ('DT', 'Defensive Tackle'),
        ('NT', 'Nose Tackle'),
        ('DE', 'Defensive End'),
        ('ILB', 'Inside Linebacker'),
        ('OLB', 'Outside Linebacker'),
        ('CB', 'Cornerback'),
        ('FS', 'Free Safety'),
        ('SS', 'Strong Safety'),
        ('K', 'Kicker'),
        ('P', 'Punter'),
        ('LS', 'Long Snapper'),
    ]

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    number = models.PositiveIntegerField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='players')
    position = models.CharField(max_length=3, choices=POSITION_CHOICES, default='QB')

    class Meta:
        unique_together = ('number', 'team')
        ordering = ['team', 'number']

    def __str__(self):
        return f"{self.first_name} {self.last_name} (#{self.number}) - {self.get_position_display()}"

    def clean(self):
        if not (0 <= self.number <= 99):
            raise ValidationError('Player number must be between 0 and 99.')


class Match(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
    ]

    WEATHER_CHOICES = [
        ('Cloudy', 'Cloudy'),
        ('Rainy', 'Rainy'),
        ('Sunny', 'Sunny'),
        ('Windy', 'Windy'),
    ]

    team1 = models.ForeignKey(Team, related_name='team1_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2_matches', on_delete=models.CASCADE)
    game_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    score_team1 = models.PositiveIntegerField(default=0)
    score_team2 = models.PositiveIntegerField(default=0)
    odds_team1 = models.FloatField(default=1.5)
    odds_team2 = models.FloatField(default=1.5)
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, default='Sunny')
    commentary = models.TextField(blank=True, default='')

    def __str__(self):
        return f'{self.team1} vs {self.team2} le {self.game_date}'

    def get_winner(self):
        if self.status == 'Completed':
            if self.score_team1 > self.score_team2:
                return self.team1
            elif self.score_team2 > self.score_team1:
                return self.team2
            return 'Draw'
        return None


class Bet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bets')
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets')
    team_choice = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    winnings = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'match')

    def __str__(self):
        return f"Pari de {self.user} sur {self.team_choice} — {self.amount}€"

    def calculate_winnings(self):
        """Calculate winnings/losses once the match is completed."""
        winner = self.match.get_winner()
        if winner is None:
            return None
        if winner == self.team_choice:
            if self.team_choice == self.match.team1:
                return float(self.amount) * self.match.odds_team1
            else:
                return float(self.amount) * self.match.odds_team2
        return -float(self.amount)


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True)
    must_change_password = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
