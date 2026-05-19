import 'package:flutter/material.dart';
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
    // Sort: Ongoing first, then Scheduled, then Completed
    bets.sort((a, b) {
      const order = {'Ongoing': 0, 'Scheduled': 1, 'Completed': 2};
      return (order[a.status] ?? 3).compareTo(order[b.status] ?? 3);
    });
    setState(() { _bets = bets; _loading = false; });
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'Ongoing': return Colors.green;
      case 'Completed': return Colors.grey;
      default: return const Color(0xFF457B9D);
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'Ongoing': return 'Ongoing';
      case 'Completed': return 'Completed';
      default: return 'Upcoming';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFABE5E5),
      appBar: AppBar(
        title: const Text('My Bets', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF7CA5A6),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: _load,
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            onPressed: () async {
              await ApiService.logout();
              if (mounted) Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _bets.isEmpty
              ? const Center(child: Text('No bets placed yet.', style: TextStyle(fontSize: 16)))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _bets.length,
                    itemBuilder: (ctx, i) {
                      final bet = _bets[i];
                      final isOngoing = bet.status == 'Ongoing';
                      return Opacity(
                        opacity: isOngoing ? 1.0 : 0.6,
                        child: Card(
                          elevation: isOngoing ? 6 : 2,
                          margin: const EdgeInsets.symmetric(vertical: 6),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                            side: isOngoing
                                ? const BorderSide(color: Colors.green, width: 2)
                                : BorderSide.none,
                          ),
                          child: ListTile(
                            contentPadding: const EdgeInsets.all(12),
                            title: Text(
                              '${bet.team1} vs ${bet.team2}',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                            ),
                            subtitle: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text('${bet.gameDate}  ${bet.startTime.substring(0, 5)} — ${bet.endTime.substring(0, 5)}'),
                                if (bet.status != 'Scheduled')
                                  Text('Score: ${bet.scoreTeam1} — ${bet.scoreTeam2}',
                                      style: const TextStyle(fontWeight: FontWeight.w600)),
                              ],
                            ),
                            trailing: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: _statusColor(bet.status),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(_statusLabel(bet.status),
                                      style: const TextStyle(color: Colors.white, fontSize: 11)),
                                ),
                              ],
                            ),
                            onTap: () => Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => MatchDetailScreen(bet: bet),
                              ),
                            ).then((_) => _load()),
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
