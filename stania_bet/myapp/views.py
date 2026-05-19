import random
import string
import json

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Match, Player, Bet, Team
from .forms import BetForm, SignUpForm, PasswordResetForm, TeamForm, PlayerForm, MatchForm, CommentaryForm

User = get_user_model()


def is_admin(user):
    return user.is_staff


# ─── Public pages ───────────────────────────────────────────────────────────

def home(request):
    today = timezone.now().date()
    upcoming_matches = Match.objects.filter(status='Scheduled', game_date=today).order_by('start_time')
    ongoing_matches = Match.objects.filter(status='Ongoing').order_by('start_time')
    return render(request, 'index.html', {
        'upcoming_matches': upcoming_matches,
        'ongoing_matches': ongoing_matches,
    })


def all_games(request):
    games_in_progress = Match.objects.filter(status='Ongoing').order_by('start_time')
    upcoming_games = Match.objects.filter(status='Scheduled').order_by('game_date', 'start_time')
    finished_games = Match.objects.filter(status='Completed').order_by('-game_date', '-start_time')
    return render(request, 'all_games.html', {
        'games_in_progress': games_in_progress,
        'upcoming_games': upcoming_games,
        'finished_games': finished_games,
    })


def game_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    team1_players = Player.objects.filter(team=match.team1)
    team2_players = Player.objects.filter(team=match.team2)
    existing_bet = None
    if request.user.is_authenticated:
        existing_bet = Bet.objects.filter(user=request.user, match=match).first()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be signed in to place a bet.")
            return redirect('signin')

        form = BetForm(match=match, data=request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            team_choice = form.cleaned_data['team_choice']

            if existing_bet:
                if amount == 0:
                    existing_bet.delete()
                    messages.success(request, "Your bet has been removed.")
                else:
                    existing_bet.amount = amount
                    existing_bet.team_choice = team_choice
                    existing_bet.save()
                    messages.success(request, "Your bet has been updated.")
            else:
                Bet.objects.create(
                    user=request.user,
                    match=match,
                    team_choice=team_choice,
                    amount=amount,
                )
                messages.success(request, "Your bet has been placed.")
            return redirect('game_detail', match_id=match.id)
    else:
        initial = {}
        if existing_bet:
            initial = {'amount': existing_bet.amount, 'team_choice': existing_bet.team_choice}
        form = BetForm(match=match, initial=initial)

    return render(request, 'game_detail.html', {
        'match': match,
        'team1_players': team1_players,
        'team2_players': team2_players,
        'form': form,
        'existing_bet': existing_bet,
    })


# ─── Betting (US5 / US6) ────────────────────────────────────────────────────

def place_bets(request):
    matches = Match.objects.filter(status='Scheduled').order_by('game_date', 'start_time')
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/signin/?next=/bet/')
        selected_ids = request.POST.getlist('selected_matches')
        bets_data = []
        for mid in selected_ids:
            try:
                m = Match.objects.get(pk=mid, status='Scheduled')
            except Match.DoesNotExist:
                continue
            bets_data.append({
                'match_id': mid,
                'match': m,
                'amount': request.POST.get(f'amount_{mid}', ''),
                'team_choice': request.POST.get(f'team_choice_{mid}', ''),
            })
        request.session['pending_bets'] = [
            {'match_id': b['match_id'], 'amount': b['amount'], 'team_choice': b['team_choice']}
            for b in bets_data
        ]
        return redirect('confirm_bets')

    return render(request, 'place_bets.html', {'matches': matches})


@login_required
def confirm_bets(request):
    pending = request.session.get('pending_bets', [])
    bets_data = []
    for item in pending:
        try:
            m = Match.objects.get(pk=item['match_id'])
            team = Team.objects.get(pk=item['team_choice']) if item['team_choice'] else None
            bets_data.append({'match': m, 'amount': item['amount'], 'team': team,
                               'match_id': item['match_id'], 'team_id': item['team_choice']})
        except (Match.DoesNotExist, Team.DoesNotExist):
            continue

    if request.method == 'POST' and request.POST.get('confirmed') == '1':
        for item in pending:
            try:
                m = Match.objects.get(pk=item['match_id'], status='Scheduled')
                team = Team.objects.get(pk=item['team_choice'])
                amount = float(item['amount'])
                if amount > 0:
                    Bet.objects.update_or_create(
                        user=request.user, match=m,
                        defaults={'team_choice': team, 'amount': amount}
                    )
            except (Match.DoesNotExist, Team.DoesNotExist, ValueError):
                continue
        del request.session['pending_bets']
        messages.success(request, "Your bets have been confirmed!")
        return redirect('user_space')

    return render(request, 'confirm_bets.html', {'bets_data': bets_data})


def bet_success(request):
    return render(request, 'bet_success.html')


# ─── User space ─────────────────────────────────────────────────────────────

@login_required
def user_space(request):
    user_bets = Bet.objects.filter(user=request.user).select_related('match', 'team_choice').order_by('-created_at')
    history = []
    for bet in user_bets.filter(match__status='Completed'):
        history.append({
            'date': bet.match.game_date.isoformat(),
            'amount': float(bet.winnings) if bet.winnings is not None else 0,
        })
    return render(request, 'user_space.html', {
        'bets': user_bets,
        'history_json': json.dumps(history),
    })


@login_required
def bet_history(request):
    user_bets = Bet.objects.filter(user=request.user).select_related(
        'match', 'match__team1', 'match__team2', 'team_choice'
    ).order_by('-created_at')
    return render(request, 'bet_history.html', {'bets': user_bets})


@login_required
def delete_bet(request, bet_id):
    bet = get_object_or_404(Bet, id=bet_id, user=request.user)
    if bet.match.status == 'Scheduled':
        bet.delete()
        messages.success(request, "Bet deleted.")
    else:
        messages.error(request, "This bet cannot be deleted.")
    return redirect('bet_history')


@login_required
def update_bet(request, bet_id):
    bet = get_object_or_404(Bet, id=bet_id, user=request.user)
    if bet.match.status != 'Scheduled':
        messages.error(request, "This match has already started.")
        return redirect('bet_history')
    return redirect('game_detail', match_id=bet.match.id)


# ─── Authentication ─────────────────────────────────────────────────────────

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            link = request.build_absolute_uri(f'/activate/{user.id}/')
            send_mail(
                'Confirm your registration — Stania Bet',
                f'Hello {user.first_name},\n\nClick this link to activate your account:\n{link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            messages.success(request, "A confirmation email has been sent.")
            return redirect('signin')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def activate_account(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, "Your account is activated. You can now sign in.")
    return redirect('signin')


def signin(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if user.must_change_password:
                return redirect('password_change')
            return redirect(request.GET.get('next', 'home'))
        messages.error(request, "Email or password incorrect.")
    return render(request, 'signin.html')


def signout(request):
    logout(request)
    return redirect('home')


@login_required
def password_change(request):
    """Forced password change after reset."""
    if request.method == 'POST':
        new_pwd = request.POST.get('password1', '')
        confirm = request.POST.get('password2', '')
        if new_pwd and new_pwd == confirm:
            request.user.set_password(new_pwd)
            request.user.must_change_password = False
            request.user.save()
            messages.success(request, "Password changed. Please sign in again.")
            return redirect('signin')
        messages.error(request, "Passwords do not match.")
    return render(request, 'password_change.html')


def password_reset(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            user = User.objects.get(last_name=last_name, email=email)
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            user.set_password(new_password)
            user.must_change_password = True
            user.save()
            send_mail(
                'Your new password — Stania Bet',
                f'Your temporary password: {new_password}\n\nPlease change it on your next login.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            messages.success(request, "A new password has been sent to your email.")
            return redirect('signin')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset.html', {'form': form})


# ─── Admin space ────────────────────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html', {
        'teams': Team.objects.all(),
        'players': Player.objects.select_related('team').all(),
        'matches': Match.objects.select_related('team1', 'team2').all().order_by('-game_date', '-start_time'),
    })


@login_required
@user_passes_test(is_admin)
def create_team(request):
    form = TeamForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Team created.")
        return redirect('admin_dashboard')
    return render(request, 'create_team.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def create_player(request):
    form = PlayerForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Player created.")
        return redirect('admin_dashboard')
    return render(request, 'create_player.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def create_match(request):
    form = MatchForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Match scheduled.")
        return redirect('admin_dashboard')
    return render(request, 'create_match.html', {'form': form})


# ─── REST API (for mobile & desktop apps) ───────────────────────────────────

@require_GET
def api_matches(request):
    matches = Match.objects.select_related('team1', 'team2').all().order_by('game_date', 'start_time')
    data = [_match_to_dict(m) for m in matches]
    return JsonResponse(data, safe=False)


@require_GET
def api_match_detail(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    data = _match_to_dict(match, detail=True)
    return JsonResponse(data)


@require_GET
def api_matches_today(request):
    today = timezone.now().date()
    matches = Match.objects.filter(game_date=today).select_related('team1', 'team2').order_by('start_time')
    return JsonResponse([_match_to_dict(m) for m in matches], safe=False)


def api_login(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    email = body.get('email', '')
    password = body.get('password', '')
    user = authenticate(request, username=email, password=password)
    if user:
        login(request, user)
        return JsonResponse({'success': True, 'user_id': user.id, 'name': f'{user.first_name} {user.last_name}'})
    return JsonResponse({'error': 'Invalid credentials'}, status=401)


@login_required
def api_user_bets(request):
    bets = Bet.objects.filter(user=request.user).select_related('match', 'match__team1', 'match__team2', 'team_choice')
    data = [_bet_to_dict(b) for b in bets]
    return JsonResponse(data, safe=False)


@csrf_exempt
def api_update_match(request, match_id):
    """Commentator endpoint: start, add commentary/score, close a match."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    match = get_object_or_404(Match, id=match_id)
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    action = body.get('action')
    if action == 'start':
        match.status = 'Ongoing'
        match.save()
    elif action == 'add_commentary':
        new_line = body.get('commentary', '').strip()
        score1 = body.get('score_team1')
        score2 = body.get('score_team2')
        if new_line:
            match.commentary = (match.commentary + '\n' + new_line).strip()
        if score1 is not None:
            match.score_team1 = int(score1)
        if score2 is not None:
            match.score_team2 = int(score2)
        match.save()
    elif action == 'close':
        match.status = 'Completed'
        match.end_time = timezone.now().time()
        match.save()
        # Calculate winnings for each bettor
        for bet in match.bets.all():
            w = bet.calculate_winnings()
            bet.winnings = w
            bet.save()
    else:
        return JsonResponse({'error': 'Unknown action'}, status=400)

    return JsonResponse({'success': True, 'match': _match_to_dict(match)})


# ─── Helpers ────────────────────────────────────────────────────────────────


def _match_to_dict(match, detail=False):
    d = {
        'id': match.id,
        'team1': str(match.team1),
        'team1_id': match.team1.id,
        'team2': str(match.team2),
        'team2_id': match.team2.id,
        'game_date': str(match.game_date),
        'start_time': str(match.start_time),
        'end_time': str(match.end_time),
        'status': match.status,
        'score_team1': match.score_team1,
        'score_team2': match.score_team2,
        'odds_team1': match.odds_team1,
        'odds_team2': match.odds_team2,
        'weather': match.weather,
        'commentary': match.commentary,
    }
    if detail:
        d['team1_players'] = [
            {'name': f'{p.first_name} {p.last_name}', 'number': p.number, 'position': p.get_position_display()}
            for p in match.team1.players.all()
        ]
        d['team2_players'] = [
            {'name': f'{p.first_name} {p.last_name}', 'number': p.number, 'position': p.get_position_display()}
            for p in match.team2.players.all()
        ]
        bets_team1 = match.bets.filter(team_choice=match.team1).count()
        bets_team2 = match.bets.filter(team_choice=match.team2).count()
        d['bets_team1_count'] = bets_team1
        d['bets_team2_count'] = bets_team2
    return d


def _bet_to_dict(bet):
    return {
        'id': bet.id,
        'match_id': bet.match.id,
        'team1': str(bet.match.team1),
        'team2': str(bet.match.team2),
        'game_date': str(bet.match.game_date),
        'start_time': str(bet.match.start_time),
        'end_time': str(bet.match.end_time),
        'status': bet.match.status,
        'score_team1': bet.match.score_team1,
        'score_team2': bet.match.score_team2,
        'commentary': bet.match.commentary,
        'team_choice': str(bet.team_choice),
        'amount': float(bet.amount),
        'winnings': float(bet.winnings) if bet.winnings is not None else None,
    }
