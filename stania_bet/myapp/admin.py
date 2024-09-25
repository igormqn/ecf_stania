from django.contrib import admin
from .models import Match

class MatchAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'game_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'game_date')
    search_fields = ('team1__name', 'team2__name')

admin.site.register(Match, MatchAdmin)
