import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from myapp.models import Team, Player, Match, Bet

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with realistic NFL demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # ── Teams ──────────────────────────────────────────────────────────
        teams_data = [
            ('Chiefs',    'Kansas City'),
            ('Eagles',    'Philadelphia'),
            ('49ers',     'San Francisco'),
            ('Ravens',    'Baltimore'),
            ('Cowboys',   'Dallas'),
            ('Dolphins',  'Miami'),
            ('Packers',   'Green Bay'),
            ('Lions',     'Detroit'),
        ]
        teams = {}
        for name, city in teams_data:
            t, _ = Team.objects.get_or_create(name=name, city=city)
            teams[name] = t
        self.stdout.write(f'  {len(teams)} teams created')

        # ── Players ────────────────────────────────────────────────────────
        players_data = {
            'Chiefs': [
                ('Patrick', 'Mahomes',  15, 'QB'),
                ('Travis',  'Kelce',    87, 'TE'),
                ('Chris',   'Jones',    95, 'DT'),
                ('Rashee',  'Rice',     4,  'WR'),
                ('Nick',    'Bolton',   32, 'ILB'),
            ],
            'Eagles': [
                ('Jalen',   'Hurts',    1,  'QB'),
                ('AJ',      'Brown',    11, 'WR'),
                ('DeVonta', 'Smith',    6,  'WR'),
                ('Jordan',  'Mailata',  68, 'T'),
                ('Saquon',  'Barkley',  26, 'RB'),
            ],
            '49ers': [
                ('Brock',   'Purdy',    13, 'QB'),
                ('Christian','McCaffrey',23,'RB'),
                ('Deebo',   'Samuel',   19, 'WR'),
                ('George',  'Kittle',   85, 'TE'),
                ('Nick',    'Bosa',     97, 'DE'),
            ],
            'Ravens': [
                ('Lamar',   'Jackson',  8,  'QB'),
                ('Derrick', 'Henry',    22, 'RB'),
                ('Zay',     'Flowers',  4,  'WR'),
                ('Mark',    'Andrews',  89, 'TE'),
                ('Roquan',  'Smith',    0,  'ILB'),
            ],
            'Cowboys': [
                ('Dak',     'Prescott', 4,  'QB'),
                ('CeeDee',  'Lamb',     88, 'WR'),
                ('Micah',   'Parsons',  11, 'OLB'),
                ('Zack',    'Martin',   70, 'G'),
                ('Rico',    'Dowdle',   23, 'RB'),
            ],
            'Dolphins': [
                ('Tua',     'Tagovailoa',1, 'QB'),
                ('Tyreek',  'Hill',     10, 'WR'),
                ('Jaylen',  'Waddle',   17, 'WR'),
                ('Jalen',   'Ramsey',   5,  'CB'),
                ('De\'Von', 'Achane',   28, 'RB'),
            ],
            'Packers': [
                ('Jordan',  'Love',     10, 'QB'),
                ('Jayden',  'Reed',     11, 'WR'),
                ('Christian','Watson',  9,  'WR'),
                ('Josh',    'Myers',    71, 'C'),
                ('Jaire',   'Alexander',23, 'CB'),
            ],
            'Lions': [
                ('Jared',   'Goff',     16, 'QB'),
                ('Amon-Ra', 'St. Brown',14, 'WR'),
                ('David',   'Montgomery',5, 'RB'),
                ('Sam',     'LaPorta',  80, 'TE'),
                ('Aidan',   'Hutchinson',97,'DE'),
            ],
        }
        player_count = 0
        for team_name, roster in players_data.items():
            team = teams[team_name]
            for first, last, number, pos in roster:
                Player.objects.get_or_create(
                    number=number, team=team,
                    defaults={'first_name': first, 'last_name': last, 'position': pos}
                )
                player_count += 1
        self.stdout.write(f'  {player_count} players created')

        # ── Matches ────────────────────────────────────────────────────────
        today = timezone.now().date()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        matches_data = [
            # Ongoing — today
            {
                'team1': teams['Chiefs'], 'team2': teams['Eagles'],
                'game_date': today, 'start_time': datetime.time(15, 0),
                'end_time': datetime.time(18, 30), 'status': 'Ongoing',
                'score_team1': 21, 'score_team2': 14,
                'odds_team1': 1.85, 'odds_team2': 2.10, 'weather': 'Sunny',
                'commentary': (
                    "Q1: Mahomes opens with a 45-yard TD pass to Kelce.\n"
                    "Q1: Eagles respond — Hurts scrambles for a 12-yard TD.\n"
                    "Q2: Mahomes finds Rice in the end zone — Chiefs lead 14-7.\n"
                    "Q2: Barkley punches it in from 3 yards out — 14-14 at the half.\n"
                    "Q3: Jones sacks Hurts, forces a fumble recovered by the Chiefs.\n"
                    "Q3: Kelce catches his second TD — Chiefs 21-14."
                ),
            },
            # Ongoing — today
            {
                'team1': teams['Ravens'], 'team2': teams['49ers'],
                'game_date': today, 'start_time': datetime.time(18, 30),
                'end_time': datetime.time(22, 0), 'status': 'Ongoing',
                'score_team1': 7, 'score_team2': 10,
                'odds_team1': 2.20, 'odds_team2': 1.70, 'weather': 'Cloudy',
                'commentary': (
                    "Q1: Lamar Jackson rushes for a 9-yard TD — Ravens 7-0.\n"
                    "Q2: Purdy hits McCaffrey on a screen — 49ers TD, 7-7.\n"
                    "Q2: Bosa sacks Jackson, Robbie Gould kicks a FG — 49ers 10-7."
                ),
            },
            # Scheduled — today
            {
                'team1': teams['Cowboys'], 'team2': teams['Dolphins'],
                'game_date': today, 'start_time': datetime.time(22, 0),
                'end_time': datetime.time(1, 30), 'status': 'Scheduled',
                'odds_team1': 1.95, 'odds_team2': 1.95, 'weather': 'Windy',
            },
            # Scheduled — tomorrow
            {
                'team1': teams['Packers'], 'team2': teams['Lions'],
                'game_date': tomorrow, 'start_time': datetime.time(19, 0),
                'end_time': datetime.time(22, 30), 'status': 'Scheduled',
                'odds_team1': 2.30, 'odds_team2': 1.65, 'weather': 'Rainy',
            },
            # Scheduled — tomorrow
            {
                'team1': teams['Chiefs'], 'team2': teams['Ravens'],
                'game_date': tomorrow, 'start_time': datetime.time(22, 30),
                'end_time': datetime.time(2, 0), 'status': 'Scheduled',
                'odds_team1': 1.75, 'odds_team2': 2.15, 'weather': 'Sunny',
            },
            # Completed — yesterday
            {
                'team1': teams['Eagles'], 'team2': teams['Cowboys'],
                'game_date': yesterday, 'start_time': datetime.time(20, 0),
                'end_time': datetime.time(23, 30), 'status': 'Completed',
                'score_team1': 34, 'score_team2': 17,
                'odds_team1': 1.80, 'odds_team2': 2.05, 'weather': 'Sunny',
                'commentary': (
                    "Q1: Hurts TD pass to AJ Brown — Eagles 7-0.\n"
                    "Q2: Prescott finds Lamb for a 38-yard TD — 7-7.\n"
                    "Q2: Barkley runs 22 yards for a TD — Eagles 14-7 at the half.\n"
                    "Q3: Smith catches his second TD of the game — 21-7.\n"
                    "Q4: Eagles pour it on — two more TDs seal the game 34-17."
                ),
            },
            # Completed — yesterday
            {
                'team1': teams['Dolphins'], 'team2': teams['Packers'],
                'game_date': yesterday, 'start_time': datetime.time(23, 0),
                'end_time': datetime.time(2, 30), 'status': 'Completed',
                'score_team1': 28, 'score_team2': 31,
                'odds_team1': 1.90, 'odds_team2': 2.00, 'weather': 'Cloudy',
                'commentary': (
                    "Q1: Hill takes the opening kick 95 yards for a TD.\n"
                    "Q2: Love throws two TD passes — Packers 14-7.\n"
                    "Q3: Achane breaks loose for a 62-yard TD run — 21-21.\n"
                    "Q4: Dramatic finish — Love hits Reed in OT for the winning score."
                ),
            },
        ]

        for data in matches_data:
            defaults = {k: v for k, v in data.items() if k not in ('team1', 'team2')}
            Match.objects.get_or_create(
                team1=data['team1'], team2=data['team2'],
                game_date=data['game_date'], defaults=defaults
            )
        self.stdout.write(f'  {len(matches_data)} matches created')

        # ── Users ──────────────────────────────────────────────────────────
        admin, created = User.objects.get_or_create(
            email='admin@staniabet.com',
            defaults={
                'username': 'admin@staniabet.com',
                'first_name': 'Admin',
                'last_name': 'Stania',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            }
        )
        if created:
            admin.set_password('admin1234!')
            admin.save()

        user1, created = User.objects.get_or_create(
            email='john@example.com',
            defaults={
                'username': 'john@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'is_active': True,
            }
        )
        if created:
            user1.set_password('pass1234!')
            user1.save()

        user2, created = User.objects.get_or_create(
            email='sarah@example.com',
            defaults={
                'username': 'sarah@example.com',
                'first_name': 'Sarah',
                'last_name': 'Connor',
                'is_active': True,
            }
        )
        if created:
            user2.set_password('pass1234!')
            user2.save()

        self.stdout.write('  3 users created')

        # ── Bets ───────────────────────────────────────────────────────────
        completed = Match.objects.filter(status='Completed')
        scheduled = Match.objects.filter(status='Scheduled')

        bet_count = 0
        for match in completed:
            Bet.objects.get_or_create(
                user=user1, match=match,
                defaults={'team_choice': match.team1, 'amount': 50}
            )
            Bet.objects.get_or_create(
                user=user2, match=match,
                defaults={'team_choice': match.team2, 'amount': 30}
            )
            bet_count += 2

        for match in scheduled[:2]:
            Bet.objects.get_or_create(
                user=user1, match=match,
                defaults={'team_choice': match.team1, 'amount': 25}
            )
            bet_count += 1

        # Calculate winnings for completed matches
        for bet in Bet.objects.filter(match__status='Completed'):
            bet.winnings = bet.calculate_winnings()
            bet.save()

        self.stdout.write(f'  {bet_count} bets created')

        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
        self.stdout.write('\nCredentials:')
        self.stdout.write('  Admin : admin@staniabet.com / admin1234!')
        self.stdout.write('  User 1: john@example.com / pass1234!')
        self.stdout.write('  User 2: sarah@example.com / pass1234!')
