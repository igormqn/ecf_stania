-- =============================================================================
-- Stania Bet — Exemple de transaction SQL
-- =============================================================================
-- Scénario : un utilisateur place un pari, puis le match se termine.
-- La transaction garantit que le pari ET les gains sont enregistrés de façon
-- atomique : si une étape échoue, tout est annulé (ROLLBACK).
-- =============================================================================

BEGIN TRANSACTION;

-- Étape 1 : Enregistrer le pari de l'utilisateur (id=1) sur le match (id=5)
--           en faveur de l'équipe (id=2) pour un montant de 50 €.
INSERT INTO myapp_bet (user_id, match_id, team_choice_id, amount, created_at, updated_at, winnings)
VALUES (1, 5, 2, 50.00, datetime('now'), datetime('now'), NULL);

-- Étape 2 : Mettre à jour le score final du match.
UPDATE myapp_match
SET score_team1 = 28,
    score_team2 = 10,
    status       = 'Completed'
WHERE id = 5;

-- Étape 3 : Calculer et enregistrer les gains.
--           Ici l'équipe gagnante est team1 (score 28 > 10).
--           Si l'utilisateur a misé sur team1, ses gains = amount * odds_team1.
--           Sinon, ses gains = -amount (perte).
--
--           Dans cet exemple : user a misé sur team_choice_id=2 (team2, perdant).
--           Gains = -50.00.
UPDATE myapp_bet
SET winnings = -50.00
WHERE user_id = 1
  AND match_id = 5;

-- Validation : si toutes les étapes précédentes ont réussi, on valide.
COMMIT;

-- =============================================================================
-- Explication de la transaction
-- =============================================================================
--
-- Une transaction regroupe plusieurs instructions SQL en une unité atomique :
--
--   BEGIN TRANSACTION : démarre la transaction ; les modifications sont
--     appliquées en mémoire mais pas encore persistées.
--
--   COMMIT : valide toutes les modifications en même temps. Si l'une des
--     étapes échoue (contrainte d'intégrité, timeout, etc.), le moteur de
--     base de données exécute automatiquement un ROLLBACK et aucune des
--     modifications n'est enregistrée.
--
--   ROLLBACK : annule toutes les modifications depuis le BEGIN TRANSACTION.
--     On peut le déclencher explicitement en cas d'erreur métier :
--
--       ROLLBACK;
--
-- Propriétés ACID garanties :
--   - Atomicité : tout ou rien.
--   - Cohérence : la base reste dans un état valide.
--   - Isolation : les autres sessions ne voient pas les changements
--                 intermédiaires (selon le niveau d'isolation configuré).
--   - Durabilité : une fois le COMMIT effectué, les données sont persistées
--                  même en cas de panne.
--
-- Dans le contexte Django, ce comportement est géré automatiquement par
-- django.db.transaction.atomic() autour de chaque vue ou opération critique.
-- =============================================================================
