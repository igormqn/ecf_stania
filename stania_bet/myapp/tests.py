import json
import datetime
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Team, Player, Match, Bet

User = get_user_model()


# ─── Helpers ─────────────────────────────────────────────────────────────────

def make_team(name='Chiefs', city='Kansas City'):
    return Team.objects.create(name=name, city=city)


def make_match(team1, team2, status='Scheduled', game_date=None):
    if game_date is None:
        game_date = timezone.now().date()
    return Match.objects.create(
        team1=team1, team2=team2,
        game_date=game_date,
        start_time=datetime.time(18, 0),
        end_time=datetime.time(21, 0),
        status=status,
        odds_team1=2.0,
        odds_team2=1.8,
    )


def make_user(email='player@test.com', password='pass1234!', is_staff=False, is_active=True):
    return User.objects.create_user(
        username=email, email=email,
        password=password,
        first_name='Test', last_name='User',
        is_staff=is_staff, is_active=is_active,
    )


# ─── Unit Tests: Models ───────────────────────────────────────────────────────

class TeamModelTest(TestCase):
    def test_str(self):
        t = make_team()
        self.assertEqual(str(t), 'Kansas City Chiefs')

    def test_unique_together(self):
        make_team()
        with self.assertRaises(Exception):
            make_team()


class PlayerModelTest(TestCase):
    def setUp(self):
        self.team = make_team()

    def test_str(self):
        p = Player.objects.create(
            first_name='Patrick', last_name='Mahomes',
            number=15, team=self.team, position='QB'
        )
        self.assertIn('Mahomes', str(p))
        self.assertIn('#15', str(p))

    def test_unique_number_per_team(self):
        Player.objects.create(first_name='A', last_name='B', number=10, team=self.team, position='QB')
        with self.assertRaises(Exception):
            Player.objects.create(first_name='C', last_name='D', number=10, team=self.team, position='RB')


class MatchModelTest(TestCase):
    def setUp(self):
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.match = make_match(self.t1, self.t2)

    def test_str_contains_teams(self):
        self.assertIn('Chiefs', str(self.match))
        self.assertIn('Eagles', str(self.match))

    def test_get_winner_not_completed(self):
        self.assertIsNone(self.match.get_winner())

    def test_get_winner_team1(self):
        self.match.status = 'Completed'
        self.match.score_team1 = 24
        self.match.score_team2 = 10
        self.match.save()
        self.assertEqual(self.match.get_winner(), self.t1)

    def test_get_winner_team2(self):
        self.match.status = 'Completed'
        self.match.score_team1 = 10
        self.match.score_team2 = 17
        self.match.save()
        self.assertEqual(self.match.get_winner(), self.t2)

    def test_get_winner_draw(self):
        self.match.status = 'Completed'
        self.match.score_team1 = 14
        self.match.score_team2 = 14
        self.match.save()
        self.assertEqual(self.match.get_winner(), 'Égalité')


class BetCalculateWinningsTest(TestCase):
    def setUp(self):
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.match = make_match(self.t1, self.t2, status='Completed')
        self.match.score_team1 = 28
        self.match.score_team2 = 10
        self.match.save()
        self.user = make_user()

    def test_winning_bet_on_team1(self):
        bet = Bet.objects.create(
            user=self.user, match=self.match,
            team_choice=self.t1, amount=Decimal('50')
        )
        self.assertAlmostEqual(bet.calculate_winnings(), 100.0)

    def test_losing_bet(self):
        bet = Bet.objects.create(
            user=self.user, match=self.match,
            team_choice=self.t2, amount=Decimal('50')
        )
        self.assertAlmostEqual(bet.calculate_winnings(), -50.0)

    def test_no_winnings_when_not_completed(self):
        self.match.status = 'Ongoing'
        self.match.save()
        bet = Bet.objects.create(
            user=self.user, match=self.match,
            team_choice=self.t1, amount=Decimal('20')
        )
        self.assertIsNone(bet.calculate_winnings())


class CustomUserModelTest(TestCase):
    def test_create_user(self):
        u = make_user('user@example.com', 'secret')
        self.assertEqual(u.email, 'user@example.com')
        self.assertFalse(u.must_change_password)

    def test_str(self):
        u = make_user('user@example.com')
        self.assertIn('Test', str(u))
        self.assertIn('user@example.com', str(u))


# ─── Unit Tests: Forms ────────────────────────────────────────────────────────

from .forms import SignUpForm, BetForm, PasswordResetForm, MatchForm


class SignUpFormTest(TestCase):
    def _base_data(self):
        return {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@test.com',
            'password1': 'Str0ng!Pass',
            'password2': 'Str0ng!Pass',
        }

    def test_valid_form(self):
        form = SignUpForm(data=self._base_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch(self):
        data = self._base_data()
        data['password2'] = 'wrong'
        form = SignUpForm(data=data)
        self.assertFalse(form.is_valid())

    def test_duplicate_email(self):
        make_user('john@test.com')
        form = SignUpForm(data=self._base_data())
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


class MatchFormTest(TestCase):
    def setUp(self):
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')

    def _base_data(self, t1_pk=None, t2_pk=None):
        return {
            'team1': t1_pk or self.t1.pk,
            'team2': t2_pk or self.t2.pk,
            'game_date': '2026-02-09',
            'start_time': '18:00',
            'end_time': '21:00',
            'odds_team1': '2.0',
            'odds_team2': '1.8',
            'weather': 'Sunny',
        }

    def test_valid(self):
        form = MatchForm(data=self._base_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_same_team_invalid(self):
        data = self._base_data(t2_pk=self.t1.pk)
        form = MatchForm(data=data)
        self.assertFalse(form.is_valid())

    def test_end_before_start_invalid(self):
        data = self._base_data()
        data['end_time'] = '17:00'
        form = MatchForm(data=data)
        self.assertFalse(form.is_valid())


class BetFormTest(TestCase):
    def setUp(self):
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.match = make_match(self.t1, self.t2)

    def test_queryset_limited_to_match_teams(self):
        form = BetForm(match=self.match)
        pks = list(form.fields['team_choice'].queryset.values_list('pk', flat=True))
        self.assertIn(self.t1.pk, pks)
        self.assertIn(self.t2.pk, pks)
        self.assertEqual(len(pks), 2)

    def test_valid_bet(self):
        form = BetForm(match=self.match, data={'amount': '50', 'team_choice': self.t1.pk})
        self.assertTrue(form.is_valid(), form.errors)

    def test_zero_amount_valid(self):
        # 0 is accepted — in game_detail it triggers bet deletion
        form = BetForm(match=self.match, data={'amount': '0', 'team_choice': self.t1.pk})
        self.assertTrue(form.is_valid())


class PasswordResetFormTest(TestCase):
    def setUp(self):
        u = make_user('jane@test.com')
        u.last_name = 'Smith'
        u.save()

    def test_valid(self):
        form = PasswordResetForm(data={'last_name': 'Smith', 'email': 'jane@test.com'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_wrong_combo(self):
        form = PasswordResetForm(data={'last_name': 'Wrong', 'email': 'jane@test.com'})
        self.assertFalse(form.is_valid())


# ─── Functional Tests: Views ──────────────────────────────────────────────────

class PublicViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.match = make_match(self.t1, self.t2)

    def test_home_accessible(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 200)

    def test_all_games_accessible(self):
        r = self.client.get(reverse('all_games'))
        self.assertEqual(r.status_code, 200)

    def test_game_detail_accessible(self):
        r = self.client.get(reverse('game_detail', args=[self.match.pk]))
        self.assertEqual(r.status_code, 200)

    def test_place_bets_visible_to_anonymous(self):
        r = self.client.get(reverse('place_bets'))
        self.assertEqual(r.status_code, 200)

    def test_signin_page(self):
        r = self.client.get(reverse('signin'))
        self.assertEqual(r.status_code, 200)

    def test_signup_page(self):
        r = self.client.get(reverse('signup'))
        self.assertEqual(r.status_code, 200)

    def test_password_reset_page(self):
        r = self.client.get(reverse('password_reset'))
        self.assertEqual(r.status_code, 200)


class AuthFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('auth@test.com', 'testpass123')

    def test_signup_creates_inactive_user(self):
        r = self.client.post(reverse('signup'), {
            'first_name': 'Alice',
            'last_name': 'Wonder',
            'email': 'alice@new.com',
            'password1': 'Str0ng!Pass',
            'password2': 'Str0ng!Pass',
        })
        self.assertRedirects(r, reverse('signin'))
        u = User.objects.get(email='alice@new.com')
        self.assertFalse(u.is_active)

    def test_activate_account(self):
        inactive = make_user('inactive@test.com', is_active=False)
        r = self.client.get(reverse('activate_account', args=[inactive.pk]))
        self.assertRedirects(r, reverse('signin'))
        inactive.refresh_from_db()
        self.assertTrue(inactive.is_active)

    def test_signin_valid(self):
        r = self.client.post(reverse('signin'), {'email': 'auth@test.com', 'password': 'testpass123'})
        self.assertRedirects(r, reverse('home'))

    def test_signin_invalid(self):
        r = self.client.post(reverse('signin'), {'email': 'auth@test.com', 'password': 'wrong'})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'incorrect')

    def test_signin_redirects_to_password_change_when_flag_set(self):
        self.user.must_change_password = True
        self.user.save()
        r = self.client.post(reverse('signin'), {'email': 'auth@test.com', 'password': 'testpass123'})
        self.assertRedirects(r, reverse('password_change'))

    def test_signout(self):
        self.client.login(username='auth@test.com', password='testpass123')
        r = self.client.get(reverse('logout'))
        self.assertRedirects(r, reverse('home'))


class PasswordChangeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('change@test.com', 'oldpass123')
        self.user.must_change_password = True
        self.user.save()
        self.client.login(username='change@test.com', password='oldpass123')

    def test_get_password_change_page(self):
        r = self.client.get(reverse('password_change'))
        self.assertEqual(r.status_code, 200)

    def test_successful_change_clears_flag(self):
        r = self.client.post(reverse('password_change'), {
            'password1': 'NewStr0ng!Pass',
            'password2': 'NewStr0ng!Pass',
        })
        self.assertRedirects(r, reverse('signin'))
        self.user.refresh_from_db()
        self.assertFalse(self.user.must_change_password)

    def test_mismatch_stays_on_page(self):
        r = self.client.post(reverse('password_change'), {
            'password1': 'NewStr0ng!Pass',
            'password2': 'different',
        })
        self.assertEqual(r.status_code, 200)

    def test_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('password_change'))
        self.assertEqual(r.status_code, 302)


class PasswordResetViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user('reset@test.com', 'oldpass')
        self.user.last_name = 'Smith'
        self.user.save()

    def test_valid_reset_sets_flag(self):
        r = self.client.post(reverse('password_reset'), {
            'last_name': 'Smith',
            'email': 'reset@test.com',
        })
        self.assertRedirects(r, reverse('signin'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.must_change_password)

    def test_invalid_combo_shows_error(self):
        r = self.client.post(reverse('password_reset'), {
            'last_name': 'Wrong',
            'email': 'reset@test.com',
        })
        self.assertEqual(r.status_code, 200)


class BettingFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.match = make_match(self.t1, self.t2)
        self.user = make_user('bettor@test.com', 'pass1234!')
        self.client.login(username='bettor@test.com', password='pass1234!')

    def test_place_bets_post_anonymous_redirects_to_signin(self):
        self.client.logout()
        r = self.client.post(reverse('place_bets'), {
            'selected_matches': [self.match.pk],
            f'amount_{self.match.pk}': '20',
            f'team_choice_{self.match.pk}': str(self.t1.pk),
        })
        self.assertIn('/signin/', r['Location'])

    def test_place_bets_logged_in_redirects_to_confirm(self):
        r = self.client.post(reverse('place_bets'), {
            'selected_matches': [self.match.pk],
            f'amount_{self.match.pk}': '20',
            f'team_choice_{self.match.pk}': str(self.t1.pk),
        })
        self.assertRedirects(r, reverse('confirm_bets'))

    def test_confirm_bets_creates_bet(self):
        session = self.client.session
        session['pending_bets'] = [
            {'match_id': str(self.match.pk), 'amount': '30', 'team_choice': str(self.t1.pk)}
        ]
        session.save()
        self.client.post(reverse('confirm_bets'), {'confirmed': '1'})
        self.assertTrue(Bet.objects.filter(user=self.user, match=self.match).exists())

    def test_game_detail_bet_submission(self):
        r = self.client.post(reverse('game_detail', args=[self.match.pk]), {
            'amount': '25',
            'team_choice': self.t1.pk,
        })
        self.assertRedirects(r, reverse('game_detail', args=[self.match.pk]))
        self.assertEqual(Bet.objects.filter(user=self.user, match=self.match).count(), 1)

    def test_user_space_requires_login(self):
        self.client.logout()
        r = self.client.get(reverse('user_space'))
        self.assertEqual(r.status_code, 302)

    def test_bet_history_shows_bets(self):
        Bet.objects.create(user=self.user, match=self.match, team_choice=self.t1, amount=Decimal('10'))
        r = self.client.get(reverse('bet_history'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Chiefs')

    def test_delete_bet_on_scheduled_match(self):
        bet = Bet.objects.create(user=self.user, match=self.match, team_choice=self.t1, amount=Decimal('10'))
        r = self.client.post(reverse('delete_bet', args=[bet.pk]))
        self.assertRedirects(r, reverse('bet_history'))
        self.assertFalse(Bet.objects.filter(pk=bet.pk).exists())

    def test_cannot_delete_bet_on_ongoing_match(self):
        self.match.status = 'Ongoing'
        self.match.save()
        bet = Bet.objects.create(user=self.user, match=self.match, team_choice=self.t1, amount=Decimal('10'))
        self.client.post(reverse('delete_bet', args=[bet.pk]))
        self.assertTrue(Bet.objects.filter(pk=bet.pk).exists())


class AdminViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.staff = make_user('admin@test.com', 'adminpass', is_staff=True)
        self.normal = make_user('user@test.com', 'userpass')

    def test_admin_dashboard_requires_staff(self):
        self.client.login(username='user@test.com', password='userpass')
        r = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(r.status_code, 302)

    def test_admin_dashboard_accessible_to_staff(self):
        self.client.login(username='admin@test.com', password='adminpass')
        r = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(r.status_code, 200)

    def test_create_team(self):
        self.client.login(username='admin@test.com', password='adminpass')
        r = self.client.post(reverse('create_team'), {'name': 'Cowboys', 'city': 'Dallas'})
        self.assertRedirects(r, reverse('admin_dashboard'))
        self.assertTrue(Team.objects.filter(name='Cowboys').exists())

    def test_create_match(self):
        self.client.login(username='admin@test.com', password='adminpass')
        r = self.client.post(reverse('create_match'), {
            'team1': self.t1.pk, 'team2': self.t2.pk,
            'game_date': '2026-02-09',
            'start_time': '18:00', 'end_time': '21:00',
            'odds_team1': '2.0', 'odds_team2': '1.8',
            'weather': 'Sunny',
        })
        self.assertRedirects(r, reverse('admin_dashboard'))
        self.assertTrue(Match.objects.filter(team1=self.t1, team2=self.t2).exists())


# ─── Functional Tests: API REST ───────────────────────────────────────────────

class ApiMatchesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.t1 = make_team('Chiefs', 'Kansas City')
        self.t2 = make_team('Eagles', 'Philadelphia')
        self.match = make_match(self.t1, self.t2)

    def test_api_matches_returns_json(self):
        r = self.client.get(reverse('api_matches'))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_api_match_detail(self):
        r = self.client.get(reverse('api_match_detail', args=[self.match.pk]))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(data['id'], self.match.pk)
        self.assertIn('team1_players', data)

    def test_api_matches_today(self):
        r = self.client.get(reverse('api_matches_today'))
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(len(data), 1)

    def test_api_login_valid(self):
        make_user('api@test.com', 'apipass')
        r = self.client.post(
            reverse('api_login'),
            data=json.dumps({'email': 'api@test.com', 'password': 'apipass'}),
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertTrue(data['success'])

    def test_api_login_invalid(self):
        r = self.client.post(
            reverse('api_login'),
            data=json.dumps({'email': 'no@one.com', 'password': 'bad'}),
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 401)

    def test_api_update_match_start(self):
        r = self.client.post(
            reverse('api_update_match', args=[self.match.pk]),
            data=json.dumps({'action': 'start'}),
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        self.match.refresh_from_db()
        self.assertEqual(self.match.status, 'Ongoing')

    def test_api_update_match_commentary(self):
        r = self.client.post(
            reverse('api_update_match', args=[self.match.pk]),
            data=json.dumps({
                'action': 'add_commentary',
                'commentary': 'Touchdown!',
                'score_team1': 7,
                'score_team2': 0,
            }),
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        self.match.refresh_from_db()
        self.assertIn('Touchdown!', self.match.commentary)
        self.assertEqual(self.match.score_team1, 7)

    def test_api_update_match_close_calculates_winnings(self):
        user = make_user('winner@test.com', 'pass')
        bet = Bet.objects.create(
            user=user, match=self.match, team_choice=self.t1, amount=Decimal('50')
        )
        self.match.score_team1 = 28
        self.match.score_team2 = 10
        self.match.save()
        r = self.client.post(
            reverse('api_update_match', args=[self.match.pk]),
            data=json.dumps({'action': 'close'}),
            content_type='application/json',
        )
        self.assertEqual(r.status_code, 200)
        bet.refresh_from_db()
        self.assertIsNotNone(bet.winnings)
        # odds_team1=2.0, amount=50, winner=team1 → winnings=100.0
        self.assertAlmostEqual(float(bet.winnings), 100.0, places=1)

    def test_api_user_bets_requires_auth(self):
        r = self.client.get(reverse('api_user_bets'))
        self.assertEqual(r.status_code, 302)
