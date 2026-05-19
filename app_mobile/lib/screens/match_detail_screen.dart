import 'dart:async';
import 'package:flutter/material.dart';
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
    // Auto-refresh every 30 seconds if the match is ongoing
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
      // Stop polling once the match is done
      if (_bet.status == 'Completed') {
        _timer?.cancel();
      }
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'Ongoing': return Colors.green;
      case 'Completed': return Colors.grey;
      default: return const Color(0xFF457B9D);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isCompleted = _bet.status == 'Completed';
    final won = _bet.winnings != null && _bet.winnings! >= 0;

    return Scaffold(
      backgroundColor: const Color(0xFFABE5E5),
      appBar: AppBar(
        title: Text('${_bet.team1} vs ${_bet.team2}',
            style: const TextStyle(color: Colors.white, fontSize: 15)),
        backgroundColor: const Color(0xFF7CA5A6),
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          if (_bet.status == 'Ongoing')
            IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white),
              onPressed: _refresh,
              tooltip: 'Refresh now',
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Status badge
              Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                  decoration: BoxDecoration(
                    color: _statusColor(_bet.status),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    _bet.status == 'Ongoing'
                        ? '🟢 Match in Progress'
                        : _bet.status == 'Completed'
                            ? '✅ Match Completed'
                            : '🕐 Upcoming',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Match info card
              _InfoCard(
                title: 'Match Info',
                children: [
                  _Row('Teams', '${_bet.team1} vs ${_bet.team2}'),
                  _Row('Date', _bet.gameDate),
                  _Row('Start', _bet.startTime.substring(0, 5)),
                  _Row('End', _bet.endTime.substring(0, 5)),
                ],
              ),

              // Score card (only if not scheduled)
              if (_bet.status != 'Scheduled')
                _InfoCard(
                  title: 'Score',
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(_bet.team1,
                            style: const TextStyle(fontWeight: FontWeight.bold)),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Text(
                            '${_bet.scoreTeam1}  —  ${_bet.scoreTeam2}',
                            style: const TextStyle(
                                fontSize: 28, fontWeight: FontWeight.bold,
                                color: Color(0xFF7CA5A6)),
                          ),
                        ),
                        Text(_bet.team2,
                            style: const TextStyle(fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ],
                ),

              // My bet card
              _InfoCard(
                title: 'My Bet',
                children: [
                  _Row('Chosen team', _bet.teamChoice),
                  _Row('Amount', '€${_bet.amount.toStringAsFixed(2)}'),
                  if (isCompleted && _bet.winnings != null)
                    _Row(
                      'Result',
                      '${won ? '+' : ''}€${_bet.winnings!.toStringAsFixed(2)}',
                      valueColor: won ? Colors.green : Colors.red,
                    ),
                ],
              ),

              // Commentary card
              if (_bet.commentary.isNotEmpty)
                Card(
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 2,
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Commentary',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
                        const Divider(),
                        Text(_bet.commentary, style: const TextStyle(fontSize: 13)),
                      ],
                    ),
                  ),
                ),

              if (_bet.status == 'Ongoing')
                const Padding(
                  padding: EdgeInsets.only(top: 12),
                  child: Center(
                    child: Text('Auto-refreshes every 30 seconds',
                        style: TextStyle(color: Colors.grey, fontSize: 12)),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const _InfoCard({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            const Divider(),
            ...children,
          ],
        ),
      ),
    );
  }
}

class _Row extends StatelessWidget {
  final String label;
  final String value;
  final Color? valueColor;
  const _Row(this.label, this.value, {this.valueColor});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value,
              style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: valueColor ?? Colors.black87)),
        ],
      ),
    );
  }
}
