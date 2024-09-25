from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Match, Player, Bet, Team
from .forms import BetForm  
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SignUpForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .forms import TeamForm, PlayerForm, MatchForm

def home(request):
    # Récupérer les matchs à venir et en cours
    upcoming_matches = Match.objects.filter(status='Scheduled').order_by('game_date')
    ongoing_matches = Match.objects.filter(status='Ongoing')

    context = {
        'upcoming_matches': upcoming_matches,
        'ongoing_matches': ongoing_matches,
    }

    return render(request, 'index.html', context)

def all_games(request):
    # Filtrer les matchs en fonction de leur statut
    games_in_progress = Match.objects.filter(status='Ongoing').order_by('game_date')
    upcoming_games = Match.objects.filter(status='Scheduled').order_by('game_date')
    finished_games = Match.objects.filter(status='Completed').order_by('-game_date')

    context = {
        'games_in_progress': games_in_progress,
        'upcoming_games': upcoming_games,
        'finished_games': finished_games,
    }

    return render(request, 'all_games.html', context)

@login_required
def game_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team1_players = Player.objects.filter(team=match.team1)
    team2_players = Player.objects.filter(team=match.team2)

    # Vérifier si une mise existe déjà pour cet utilisateur et ce match
    existing_bet = Bet.objects.filter(user=request.user, match=match).first()

    if request.method == 'POST':
        form = BetForm(request.POST)
        if form.is_valid():
            bet_amount = form.cleaned_data['amount']
            team_choice = form.cleaned_data['team_choice']

            if existing_bet:
                # Mise à jour de la mise existante
                existing_bet.amount = bet_amount
                existing_bet.team_choice = team_choice
                if bet_amount == 0:  # Si le montant est 0, supprimez la mise
                    existing_bet.delete()
                    return redirect('game_detail', match_id=match.id)
                existing_bet.save()
            else:
                # Création d'une nouvelle mise
                Bet.objects.create(
                    user=request.user,
                    match=match,
                    team_choice=team_choice,
                    amount=bet_amount
                )
            return redirect('game_detail', match_id=match.id)

    else:
        form = BetForm(initial={'amount': existing_bet.amount if existing_bet else 0, 
                                 'team_choice': existing_bet.team_choice if existing_bet else None})

    context = {
        'match': match,
        'team1_players': team1_players,
        'team2_players': team2_players,
        'form': form,
        'existing_bet': existing_bet,
    }


@login_required
def place_bets(request):
    if request.method == 'POST':
        selected_matches = request.POST.getlist('selected_matches')
        bets_data = []
        
        for match_id in selected_matches:
            amount = request.POST.get(f'amount_{match_id}')
            team_choice = request.POST.get(f'team_choice_{match_id}')
            if amount and team_choice:
                bets_data.append({
                    'match_id': match_id,
                    'amount': amount,
                    'team_choice': team_choice,
                })
        
        # Passer les données à la page de confirmation
        context = {
            'bets_data': bets_data,
        }
        return render(request, 'confirm_bets.html', context)  # Redirige vers la page de confirmation des paris

    matches = Match.objects.filter(status='Scheduled')  # Ou un autre statut selon votre logique
    context = {
        'matches': matches,
    }
    return render(request, 'place_bets.html', context)

def bet_success(request):
    return render(request, 'bet_success.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Match, Bet

@login_required
def confirm_bets(request):
    if request.method == 'POST':
        selected_matches = request.POST.getlist('selected_matches')
        bets_data = []
        for match_id in selected_matches:
            amount = request.POST.get(f'amount_{match_id}')
            team_choice = request.POST.get(f'team_choice_{match_id}')
            if amount and team_choice:
                bets_data.append({
                    'match_id': match_id,
                    'amount': amount,
                    'team_choice': team_choice,
                })
        
        # Passer les données à la page de confirmation
        context = {
            'bets_data': bets_data,
        }
        return render(request, 'confirm_bets.html', context)

    return redirect('place_bets')  # Redirigez vers la page de mise

@login_required
def finalize_bets(request):
    if request.method == 'POST':
        for match_id in request.POST.getlist('match_ids'):
            amount = request.POST.get(f'amount_{match_id}')
            team_choice = request.POST.get(f'team_choice_{match_id}')
            if amount and team_choice:
                # Crée ou met à jour le pari
                Bet.objects.update_or_create(
                    user=request.user,
                    match_id=match_id,
                    defaults={'amount': amount, 'team_choice': team_choice}
                )
        
        return redirect('bet_success')  # Redirigez vers la page de succès

    return redirect('place_bets')  # Redirigez vers la page de mise

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Désactiver jusqu'à confirmation par e-mail
            user.save()

            # Envoyer un e-mail de confirmation
            subject = 'Confirmez votre inscription'
            message = f'Suivez ce lien pour activer votre compte : {request.build_absolute_uri("/activate/")}{user.id}/'
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            messages.success(request, "Un e-mail de confirmation a été envoyé.")
            return redirect('signin')  # Rediriger vers la page de connexion
    else:
        form = SignUpForm()
    
    return render(request, 'signup.html', {'form': form})


def activate_account(request, user_id):
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, "You account was created with success. You can signin")
    return redirect('signin')

def user_space(request):
    if not request.user.is_authenticated:
        return redirect('signin')  # Redirigez vers la page de connexion si l'utilisateur n'est pas authentifié

    user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculer les gains/pertes pour le graphique
    data = []
    for bet in user_bets:
        result = bet.result
        amount = bet.amount if result == 'won' else -bet.amount
        data.append((bet.created_at.date(), amount))
    
    # Group by date
    history = {}
    for date, amount in data:
        if date not in history:
            history[date] = 0
        history[date] += amount

    context = {
        'user': request.user,
        'bets': user_bets,
        'history': history,
    }
    
    return render(request, 'user_space.html', context)

def bet_history(request):
    if not request.user.is_authenticated:
        return redirect('signin')  # Redirection vers la page de connexion

    user_bets = Bet.objects.filter(user=request.user).order_by('-created_at')
    
    # Filtrer les matchs pour obtenir les détails
    bets_with_matches = []
    for bet in user_bets:
        match = bet.match  # Assurez-vous que vous avez un champ "match" dans votre modèle Bet
        bets_with_matches.append({
            'bet': bet,
            'team_names': f"{match.team_a} vs {match.team_b}",  # Adapter selon votre modèle
            'match_date': match.date,
            'start_time': match.start_time,
            'end_time': match.end_time,
        })

    context = {
        'bets_with_matches': bets_with_matches,
    }
    
    return render(request, 'bet_history.html', context)

def delete_bet(request, bet_id):
    if request.method == 'DELETE':
        try:
            bet = Bet.objects.get(id=bet_id, user=request.user)
            bet.delete()
            return JsonResponse({'success': True})
        except Bet.DoesNotExist:
            return JsonResponse({'success': False}, status=404)

def admin_dashboard(request):
    teams = Team.objects.all()
    players = Player.objects.all()
    matches = Match.objects.all()
    context = {
        'teams': teams,
        'players': players,
        'matches': matches,
    }
    return render(request, 'admin_dashboard.html', context)

def create_team(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = TeamForm()
    return render(request, 'create_team.html', {'form': form})

def create_player(request):
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = PlayerForm()
    return render(request, 'create_player.html', {'form': form})

def create_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = MatchForm()
    return render(request, 'create_match.html', {'form': form})