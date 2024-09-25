# Generated by Django 5.1.1 on 2024-09-25 19:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('city', models.CharField(default='Unknown', max_length=100)),
            ],
            options={
                'ordering': ['name'],
                'unique_together': {('name', 'city')},
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game_date', models.DateTimeField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('status', models.CharField(choices=[('Scheduled', 'Scheduled'), ('Ongoing', 'Ongoing'), ('Completed', 'Completed')], default='Scheduled', max_length=20)),
                ('score_team1', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('score_team2', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('odds_team1', models.FloatField(default=1.0)),
                ('odds_team2', models.FloatField(default=1.0)),
                ('weather', models.CharField(choices=[('Cloudy', 'Cloudy'), ('Rainy', 'Rainy'), ('Sunny', 'Sunny'), ('Windy', 'Windy')], default='Cloudy', max_length=20)),
                ('commentary', models.TextField(default='No commentary available')),
                ('team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team1_matches', to='myapp.team')),
                ('team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team2_matches', to='myapp.team')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('number', models.PositiveIntegerField()),
                ('position', models.CharField(choices=[('QB', 'Quarterback'), ('RB', 'Running Back'), ('FB', 'Fullback'), ('WR', 'Wide Receiver'), ('TE', 'Tight End'), ('G', 'Guard'), ('T', 'Tackle'), ('C', 'Center'), ('DT', 'Defensive Tackle'), ('NT', 'Nose Tackle'), ('DE', 'Defensive End'), ('ILB', 'Inside Linebacker'), ('OLB', 'Outside Linebacker'), ('CB', 'Cornerback'), ('FS', 'Free Safety'), ('SS', 'Strong Safety'), ('K', 'Kicker'), ('P', 'Punter'), ('LS', 'Long Snapper')], default='QB', max_length=3)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='players', to='myapp.team')),
            ],
            options={
                'ordering': ['team', 'number'],
                'unique_together': {('number', 'team')},
            },
        ),
        migrations.CreateModel(
            name='Bet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.match')),
                ('team_choice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.team')),
            ],
            options={
                'unique_together': {('user', 'match')},
            },
        ),
    ]