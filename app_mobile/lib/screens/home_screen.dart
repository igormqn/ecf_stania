import 'package:flutter/material.dart';
import '../main.dart';
import '../models/bet.dart';
import '../services/api_service.dart';
import 'match_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Bet> _bets = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final bets = await ApiService.getUserBets();
    bets.sort((a, b) {
      const order = {'Ongoing': 0, 'Scheduled': 1, 'Completed': 2};
      return (order[a.status] ?? 3).compareTo(order[b.status] ?? 3);
    });
    setState(() { _bets = bets; _loading = false; });
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'Ongoing':   return kOrange;
      case 'Completed': return kTextSecondary;
      default:          return kCyan400;
    }
  }

  Color _statusBg(String status) {
    switch (status) {
      case 'Ongoing':   return kOrange.withOpacity(0.15);
      case 'Completed': return kTextSecondary.withOpacity(0.1);
      default:          return kCyan400.withOpacity(0.12);
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'Ongoing':   return 'Ongoing';
      case 'Completed': return 'Completed';
      default:          return 'Upcoming';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kNavy900,
      appBar: AppBar(
        title: const Text('My Bets'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _load,
            tooltip: 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.logout_rounded),
            tooltip: 'Logout',
            onPressed: () async {
              await ApiService.logout();
              if (mounted) Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator(color: kGold500))
          : _bets.isEmpty
              ? const Center(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.sports_football_outlined,
                          size: 56, color: kTextSecondary),
                      SizedBox(height: 16),
                      Text('No bets placed yet.',
                          style: TextStyle(color: kTextSecondary, fontSize: 16)),
                    ],
                  ),
                )
              : RefreshIndicator(
                  color: kGold500,
                  backgroundColor: kSurface,
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
                    itemCount: _bets.length,
                    itemBuilder: (ctx, i) {
                      final bet = _bets[i];
                      final isOngoing = bet.status == 'Ongoing';
                      return Opacity(
                        opacity: bet.status == 'Completed' ? 0.65 : 1.0,
                        child: GestureDetector(
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                                builder: (_) => MatchDetailScreen(bet: bet)),
                          ).then((_) => _load()),
                          child: Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            decoration: BoxDecoration(
                              color: kSurface,
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: isOngoing
                                    ? kOrange.withOpacity(0.5)
                                    : kBorder,
                                width: isOngoing ? 1.5 : 1,
                              ),
                            ),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          '${bet.team1} vs ${bet.team2}',
                                          style: const TextStyle(
                                            color: kTextPrimary,
                                            fontWeight: FontWeight.w700,
                                            fontSize: 15,
                                          ),
                                        ),
                                      ),
                                      // Status badge
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                            horizontal: 10, vertical: 4),
                                        decoration: BoxDecoration(
                                          color: _statusBg(bet.status),
                                          borderRadius: BorderRadius.circular(999),
                                          border: Border.all(
                                              color: _statusColor(bet.status)
                                                  .withOpacity(0.4)),
                                        ),
                                        child: Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            if (isOngoing) ...[
                                              Container(
                                                width: 6, height: 6,
                                                decoration: BoxDecoration(
                                                  color: kOrange,
                                                  shape: BoxShape.circle,
                                                ),
                                              ),
                                              const SizedBox(width: 5),
                                            ],
                                            Text(
                                              _statusLabel(bet.status),
                                              style: TextStyle(
                                                color: _statusColor(bet.status),
                                                fontSize: 11,
                                                fontWeight: FontWeight.w700,
                                                letterSpacing: 0.5,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    '${bet.gameDate}  ·  ${bet.startTime.substring(0, 5)} — ${bet.endTime.substring(0, 5)}',
                                    style: const TextStyle(
                                        color: kTextSecondary, fontSize: 12),
                                  ),
                                  if (bet.status != 'Scheduled') ...[
                                    const SizedBox(height: 8),
                                    Center(
                                      child: Text(
                                        '${bet.scoreTeam1}  —  ${bet.scoreTeam2}',
                                        style: const TextStyle(
                                          color: kGold400,
                                          fontSize: 22,
                                          fontWeight: FontWeight.w900,
                                          letterSpacing: 2,
                                        ),
                                      ),
                                    ),
                                  ],
                                  if (bet.status == 'Completed' &&
                                      bet.winnings != null) ...[
                                    const SizedBox(height: 8),
                                    Center(
                                      child: Text(
                                        bet.winnings! >= 0
                                            ? '+€${bet.winnings!.toStringAsFixed(2)}'
                                            : '−€${bet.winnings!.abs().toStringAsFixed(2)}',
                                        style: TextStyle(
                                          color: bet.winnings! >= 0
                                              ? kGreen : kRed,
                                          fontWeight: FontWeight.w800,
                                          fontSize: 15,
                                        ),
                                      ),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
