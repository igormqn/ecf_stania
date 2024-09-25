from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('allgames/', views.all_games, name='all_games'),
    path('game/<int:match_id>/', views.game_detail, name='game_detail'),
    path('bet/', views.place_bets, name='place_bets'),
    path('bet_success/', views.bet_success, name='bet_success'),
    path('place_bets/', views.place_bets, name='place_bets'),
    path('confirm_bets/', views.confirm_bets, name='confirm_bets'),
    path('finalize_bets/', views.finalize_bets, name='finalize_bets'),
    path('signup/', views.signup, name='signup'),
    path('activate/<int:user_id>/', views.activate_account, name='activate_account'),
    path('password_reset/', views.password_reset, name='password_reset'),   
    path('bet_history/', views.bet_history, name='bet_history'),
    path('delete_bet/<int:bet_id>/', views.delete_bet, name='delete_bet'),
    path('update_bet/<int:bet_id>/', views.update_bet, name='update_bet'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create_team/', views.create_team, name='create_team'),
    path('create_player/', views.create_player, name='create_player'),
    path('create_match/', views.create_match, name='create_match'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)