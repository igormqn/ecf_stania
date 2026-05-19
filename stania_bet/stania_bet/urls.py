from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Public pages
    path('', views.home, name='home'),
    path('allgames/', views.all_games, name='all_games'),
    path('game/<int:match_id>/', views.game_detail, name='game_detail'),

    # Betting
    path('bet/', views.place_bets, name='place_bets'),
    path('confirm_bets/', views.confirm_bets, name='confirm_bets'),
    path('bet_success/', views.bet_success, name='bet_success'),

    # User space
    path('espace/', views.user_space, name='user_space'),
    path('historique/', views.bet_history, name='bet_history'),
    path('delete_bet/<int:bet_id>/', views.delete_bet, name='delete_bet'),
    path('update_bet/<int:bet_id>/', views.update_bet, name='update_bet'),

    # Authentication
    path('signup/', views.signup, name='signup'),
    path('activate/<int:user_id>/', views.activate_account, name='activate_account'),
    path('signin/', views.signin, name='signin'),
    path('logout/', views.signout, name='logout'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('password_change/', views.password_change, name='password_change'),

    # Admin space
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create_team/', views.create_team, name='create_team'),
    path('create_player/', views.create_player, name='create_player'),
    path('create_match/', views.create_match, name='create_match'),

    # REST API (for mobile & desktop apps)
    path('api/matches/', views.api_matches, name='api_matches'),
    path('api/matches/today/', views.api_matches_today, name='api_matches_today'),
    path('api/matches/<int:match_id>/', views.api_match_detail, name='api_match_detail'),
    path('api/matches/<int:match_id>/update/', views.api_update_match, name='api_update_match'),
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/bets/', views.api_user_bets, name='api_user_bets'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'myapp' / 'static')
