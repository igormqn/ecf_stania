class Bet {
  final int id;
  final int matchId;
  final String team1;
  final String team2;
  final String gameDate;
  final String startTime;
  final String endTime;
  final String status;
  final int scoreTeam1;
  final int scoreTeam2;
  final String commentary;
  final String teamChoice;
  final double amount;
  final double? winnings;

  const Bet({
    required this.id,
    required this.matchId,
    required this.team1,
    required this.team2,
    required this.gameDate,
    required this.startTime,
    required this.endTime,
    required this.status,
    required this.scoreTeam1,
    required this.scoreTeam2,
    required this.commentary,
    required this.teamChoice,
    required this.amount,
    this.winnings,
  });

  factory Bet.fromJson(Map<String, dynamic> json) => Bet(
        id: json['id'],
        matchId: json['match_id'],
        team1: json['team1'],
        team2: json['team2'],
        gameDate: json['game_date'],
        startTime: json['start_time'],
        endTime: json['end_time'],
        status: json['status'],
        scoreTeam1: json['score_team1'],
        scoreTeam2: json['score_team2'],
        commentary: json['commentary'] ?? '',
        teamChoice: json['team_choice'],
        amount: (json['amount'] as num).toDouble(),
        winnings: json['winnings'] != null
            ? (json['winnings'] as num).toDouble()
            : null,
      );
}
