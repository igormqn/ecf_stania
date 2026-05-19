# Stania Bet — Super Bowl Betting Platform

ECF project — three-tier application (web Django, mobile Flutter, desktop tkinter).

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| pip | latest |
| Flutter SDK | 3.x |
| Dart | bundled with Flutter |

---

## 1. Django Web Application

### Setup

```bash
# 1. Create and activate a virtual environment
python -m venv env
# Windows
env\Scripts\activate
# macOS / Linux
source env/bin/activate

# 2. Install dependencies
pip install django pillow

# 3. Enter the Django project directory
cd stania_bet

# 4. Apply migrations
python manage.py migrate

# 5. Create a superuser (admin)
python manage.py createsuperuser

# 6. Run the development server
python manage.py runserver
```

The application is accessible at **http://127.0.0.1:8000**

### Run Tests

```bash
cd stania_bet
python manage.py test myapp
```

65 tests covering models, forms, views (auth, betting, admin) and REST API endpoints.

### Key URLs

| URL | Description |
|-----|-------------|
| `/` | Home — today's matches |
| `/allgames/` | All matches (ongoing / upcoming / completed) |
| `/game/<id>/` | Match detail + bet form |
| `/bet/` | Multi-match betting page |
| `/confirm_bets/` | Confirm pending bets |
| `/espace/` | User dashboard (bets, history, graph) |
| `/historique/` | Full bet history |
| `/signup/` | User registration |
| `/signin/` | Login |
| `/password_reset/` | Password reset (last name + email) |
| `/admin_dashboard/` | Staff-only admin panel |
| `/create_team/` | Create a team (staff only) |
| `/create_player/` | Add a player (staff only) |
| `/create_match/` | Schedule a match (staff only) |
| `/admin/` | Django admin |

### REST API (used by mobile & desktop apps)

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/matches/` | All matches |
| GET | `/api/matches/today/` | Today's matches |
| GET | `/api/matches/<id>/` | Match detail (players, bet counts) |
| POST | `/api/matches/<id>/update/` | Start / add commentary / close |
| POST | `/api/login/` | Login (JSON `{email, password}`) |
| GET | `/api/bets/` | Authenticated user's bets |

---

## 2. Desktop Application (tkinter)

The desktop app is intended for commentators: start matches, update scores/commentary, close matches.

### Setup

```bash
cd app_bureautique

# Install the only dependency
pip install requests

# Make sure the Django server is running on port 8000, then:
python app.py
```

A login window appears. Use your staff account credentials.  
After login, today's matches are listed. Select one to manage it.

---

## 3. Mobile Application (Flutter)

The mobile app lets users follow their bets in real time (auto-refresh every 30 seconds).

### Setup

```bash
cd app_mobile

# Install Flutter packages
flutter pub get

# Run on an emulator or physical device
flutter run
```

> **Note:** The Django server address is hardcoded to `http://10.0.2.2:8000` (Android emulator → localhost mapping). For a physical device or iOS simulator, update `_baseUrl` in `lib/services/api_service.dart` to your machine's local IP (e.g. `http://192.168.1.x:8000`).

---

## Project Structure

```
ECF_Stania_Bet/
├── stania_bet/             # Django project
│   ├── myapp/
│   │   ├── models.py       # Team, Player, Match, Bet, CustomUser
│   │   ├── views.py        # All views + REST API endpoints
│   │   ├── forms.py        # SignUpForm, BetForm, MatchForm, …
│   │   ├── admin.py        # Django admin configuration
│   │   ├── tests.py        # 65 unit + functional tests
│   │   ├── templates/      # All HTML templates
│   │   └── static/css/     # styles.css
│   └── stania_bet/
│       ├── settings.py
│       └── urls.py
├── app_bureautique/
│   ├── app.py              # tkinter desktop application (English)
│   └── requirements.txt
├── app_mobile/
│   ├── pubspec.yaml
│   └── lib/
│       ├── main.dart
│       ├── models/bet.dart
│       ├── services/api_service.dart
│       └── screens/
│           ├── login_screen.dart
│           ├── home_screen.dart
│           └── match_detail_screen.dart
├── transaction.sql         # SQL transaction example with explanation
└── README.md
```

---

## Features Implemented

| User Story | Description | Status |
|-----------|-------------|--------|
| US1 | View scheduled matches on home page | Done |
| US2 | View all matches (ongoing / upcoming / completed) | Done |
| US3 | User registration with email confirmation | Done |
| US4 | Login / logout | Done |
| US5 | Place bets (multi-match, with confirmation) | Done |
| US6 | View bet history in personal space | Done |
| US7 | Admin: manage teams, players, matches | Done |
| US8 | Commentator: start match, update scores, close | Done |
| US9 | Password reset via last name + email | Done |
| US10 | Mobile: follow bets with 30s auto-refresh | Done |

---

## Notes

- **Email sending**: configured with `EMAIL_BACKEND = console` in development — emails are printed to the terminal. Switch to an SMTP backend for production.
- **Database**: SQLite in development (`db.sqlite3`). For production, configure PostgreSQL in `settings.py`.
- **Static files**: run `python manage.py collectstatic` before deploying to production.
