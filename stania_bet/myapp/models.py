from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
# Modèle Team
class Team(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, default='Unknown')

    class Meta:
        unique_together = ('name', 'city')
        ordering = ['name']

    def __str__(self):
        return f"{self.city} {self.name}"

    def get_players_by_position(self, position):
        return self.players.filter(position=position)


# Modèle Player
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
        # Valider que le numéro est entre 0 et 99
        if not (0 <= self.number <= 99):
            raise ValidationError('Player number must be between 0 and 99.')


# Modèle Match
class Match(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
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
    game_date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    score_team1 = models.PositiveIntegerField(default=0, null=True, blank=True)
    score_team2 = models.PositiveIntegerField(default=0, null=True, blank=True)
    odds_team1 = models.FloatField(default=1.0)
    odds_team2 = models.FloatField(default=1.0)
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, default='Cloudy')
    commentary = models.TextField(default='No commentary available')

    def __str__(self):
        return f'{self.team1} vs {self.team2} on {self.game_date}'

    def clean(self):
        # Ensure that start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time.')
        
        # Ensure that game_date is not in the past when setting up the match
        if self.game_date < timezone.now():
            raise ValidationError('The game date cannot be in the past.')

    def save(self, *args, **kwargs):
        # Determine status based on the current time and match times
        current_time = timezone.now().time()
        if self.game_date.date() > timezone.now().date():
            self.status = 'Scheduled'
        elif self.game_date.date() == timezone.now().date():
            if self.start_time <= current_time <= self.end_time:
                self.status = 'Ongoing'
            elif current_time > self.end_time:
                self.status = 'Completed'
        else:
            self.status = 'Completed'
        
        super().save(*args, **kwargs)

    def get_winner(self):
        if self.status == 'Completed':
            if self.score_team1 > self.score_team2:
                return self.team1
            elif self.score_team2 > self.score_team1:
                return self.team2
            else:
                return 'Draw'
        return 'Game not completed yet'


# Modèle Bet
class Bet(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    team_choice = models.ForeignKey(Team, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'match')

    def clean(self):
        # Vérifier que le choix de l'équipe est bien l'une des équipes du match
        if self.team_choice not in [self.match.team1, self.match.team2]:
            raise ValidationError('Team choice must be one of the teams playing the match.')

    def __str__(self):
        return f"Bet by {self.user} on {self.team_choice} for {self.amount} USD"


class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=30, blank=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False) 