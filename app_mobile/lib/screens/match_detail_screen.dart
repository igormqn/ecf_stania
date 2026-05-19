import 'dart:async';
import 'package:flutter/material.dart';
import '../main.dart';
import '../models/bet.dart';
import '../services/api_service.dart';

class MatchDetailScreen extends StatefulWidget {
  final Bet bet;
  const MatchDetailScreen({super.key, required this.bet});
  @override
  State<MatchDetailScreen> createState() => _MatchDetailScreenState();
}

class _MatchDetailScreenState extends State<MatchDetailScreen> {
  late Bet _bet;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _bet = widget.bet;
    if (_bet.status == 'Ongoing') {
      _timer = Timer.periodic(const Duration(seconds: 30), (_) => _refresh());
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _refresh() async {
    final updated = await ApiService.getMatchBetDetail(_bet.matchId);
    if (updated != null && mounted) {
      setState(() => _bet = updated);
      if (_bet.status == 'Completed') _timer?.cancel();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCompleted = _bet.status == 'Completed';
    final won = _bet.winnings != null && _bet.winnings! >= 0;

    return Scaffold(
      backgroundColor: kNavy900,
      appBar: AppBar(
        title: Text('${_bet.team1} vs ${_bet.team2}'),
        actions: [
          if (_bet.status == 'Ongoing')
            IconButton(
              icon: const Icon(Icons.refresh_rounded),
              onPressed: _refresh,
              tooltip: 'Refresh',
            ),
        ],
      ),
      body: RefreshIndicator(
        color: kGold500,
        backgroundColor: kSurface,
        onRefresh: _refresh,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.fromLTRB(16, 20, 16, 32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Status badge
              _StatusBadge(status: _bet.status),
              const SizedBox(height: 20),

              // Score (if started)
              if (_bet.status != 'Scheduled') ...[
                _ScoreCard(bet: _bet),
                const SizedBox(height: 14),
              ],

              // Match info
              _DarkCard(
                title: 'Match Info',
                icon: Icons.info_outline_rounded,
                children: [
                  _InfoRow('Date', _bet.gameDate),
                  _InfoRow('Start', _bet.startTime.substring(0, 5)),
                  _InfoRow('End',   _bet.endTime.substring(0, 5)),
                ],
              ),
              const SizedBox(height: 14),

              // My bet
              _DarkCard(
                title: 'My Bet',
                icon: Icons.sports_football_outlined,
                children: [
                  _InfoRow('Team chosen', _bet.teamChoice),
                  _InfoRow('Stake', '€${_bet.amount.toStringAsFixed(2)}'),
                  if (isCompleted && _bet.winnings != null)
                    _InfoRow(
                      'Result',
                      '${won ? '+' : ''}€${_bet.winnings!.toStringAsFixed(2)}',
                      valueColor: won ? kGreen : kRed,
                    ),
                ],
              ),

              // Commentary
              if (_bet.commentary.isNotEmpty) ...[
                const SizedBox(height: 14),
                _CommentaryCard(text: _bet.commentary),
              ],

              // Auto-refresh hint
              if (_bet.status == 'Ongoing') ...[
                const SizedBox(height: 16),
                const Center(
                  child: Text(
                    'Auto-refreshes every 30 seconds',
                    style: TextStyle(color: kTextSecondary, fontSize: 12),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

// ── Sub-widgets ───────────────────────────────────────────────────────────────

class _StatusBadge extends StatelessWidget {
  final String status;
  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    final isOngoing   = status == 'Ongoing';
    final isCompleted = status == 'Completed';
    final color = isOngoing ? kOrange : isCompleted ? kTextSecondary : kCyan400;
    final label = isOngoing
        ? 'Match in Progress'
        : isCompleted ? 'Match Completed' : 'Upcoming';

    return Center(
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (isOngoing) ...[
              Container(
                width: 8, height: 8,
                decoration: BoxDecoration(color: kOrange, shape: BoxShape.circle),
              ),
              const SizedBox(width: 8),
            ],
            Text(label,
                style: TextStyle(
                    color: color, fontWeight: FontWeight.w700, fontSize: 13)),
          ],
        ),
      ),
    );
  }
}

class _ScoreCard extends StatelessWidget {
  final Bet bet;
  const _ScoreCard({required this.bet});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        color: kSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: kGold500.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          const Text('SCORE',
              style: TextStyle(
                  color: kTextSecondary,
                  fontSize: 11,
                  letterSpacing: 2,
                  fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: Text(bet.team1,
                    textAlign: TextAlign.end,
                    style: const TextStyle(
                        color: kTextPrimary, fontWeight: FontWeight.w700)),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Text(
                  '${bet.scoreTeam1}  —  ${bet.scoreTeam2}',
                  style: const TextStyle(
                    color: kGold400,
                    fontSize: 32,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 3,
                  ),
                ),
              ),
              Expanded(
                child: Text(bet.team2,
                    textAlign: TextAlign.start,
                    style: const TextStyle(
                        color: kTextPrimary, fontWeight: FontWeight.w700)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DarkCard extends StatelessWidget {
  final String title;
  final IconData icon;
  final List<Widget> children;
  const _DarkCard({required this.title, required this.icon, required this.children});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: kSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: kBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: kGold500, size: 16),
              const SizedBox(width: 8),
              Text(title,
                  style: const TextStyle(
                      color: kGold400,
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      letterSpacing: 0.5)),
            ],
          ),
          const SizedBox(height: 12),
          Divider(color: kBorder, height: 1),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }
}

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;
  const _InfoRow(this.label, this.value, {this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 5),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: kTextSecondary, fontSize: 13)),
          Text(value,
              style: TextStyle(
                color: valueColor ?? kTextPrimary,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              )),
        ],
      ),
    );
  }
}

class _CommentaryCard extends StatelessWidget {
  final String text;
  const _CommentaryCard({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: kSurface,
        borderRadius: BorderRadius.circular(16),
        border: Border(
          left: BorderSide(color: kGold500, width: 3),
          top: BorderSide(color: kBorder),
          right: BorderSide(color: kBorder),
          bottom: BorderSide(color: kBorder),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.mic_rounded, color: kGold500, size: 16),
              SizedBox(width: 8),
              Text('Commentary',
                  style: TextStyle(
                      color: kGold400,
                      fontWeight: FontWeight.w700,
                      fontSize: 13,
                      letterSpacing: 0.5)),
            ],
          ),
          const SizedBox(height: 12),
          Text(text,
              style: const TextStyle(
                  color: kTextSecondary, fontSize: 13, height: 1.8)),
        ],
      ),
    );
  }
}
