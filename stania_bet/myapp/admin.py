from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Team, Player, Match, Bet, CustomUser


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'city')
    search_fields = ('name', 'city')


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'number', 'position', 'team')
    list_filter = ('team', 'position')
    search_fields = ('first_name', 'last_name')


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'game_date', 'start_time', 'end_time', 'status', 'score_team1', 'score_team2')
    list_filter = ('status', 'game_date')
    search_fields = ('team1__name', 'team2__name')
    list_editable = ('status', 'score_team1', 'score_team2')


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'team_choice', 'amount', 'winnings', 'created_at')
    list_filter = ('match__status',)
    search_fields = ('user__email',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        ('Stania Bet', {'fields': ('must_change_password',)}),
    )
