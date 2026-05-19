import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/bet.dart';

class ApiService {
  static const String _baseUrl = 'http://127.0.0.1:8000';
  static String? _sessionCookie;

  static Future<bool> login(String email, String password) async {
    final r = await http.post(
      Uri.parse('$_baseUrl/api/login/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    if (r.statusCode == 200) {
      _sessionCookie = r.headers['set-cookie'];
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('session', _sessionCookie ?? '');
      await prefs.setString('user_name', jsonDecode(r.body)['name'] ?? '');
      return true;
    }
    return false;
  }

  static Future<void> _loadSession() async {
    if (_sessionCookie != null) return;
    final prefs = await SharedPreferences.getInstance();
    _sessionCookie = prefs.getString('session');
  }

  static Future<List<Bet>> getUserBets() async {
    await _loadSession();
    final r = await http.get(
      Uri.parse('$_baseUrl/api/bets/'),
      headers: {'Cookie': _sessionCookie ?? ''},
    );
    if (r.statusCode == 200) {
      final List<dynamic> data = jsonDecode(r.body);
      return data.map((j) => Bet.fromJson(j)).toList();
    }
    return [];
  }

  static Future<Bet?> getMatchBetDetail(int matchId) async {
    await _loadSession();
    // Re-use user bets and filter
    final bets = await getUserBets();
    try {
      return bets.firstWhere((b) => b.matchId == matchId);
    } catch (_) {
      return null;
    }
  }

  static Future<String?> signup({
    required String email,
    required String password,
    required String firstName,
    required String lastName,
  }) async {
    try {
      final r = await http.post(
        Uri.parse('$_baseUrl/api/signup/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password': password,
          'first_name': firstName,
          'last_name': lastName,
        }),
      );
      if (r.statusCode == 200) {
        _sessionCookie = r.headers['set-cookie'];
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('session', _sessionCookie ?? '');
        await prefs.setString('user_name', jsonDecode(r.body)['name'] ?? '');
        return null; // success
      }
      return jsonDecode(r.body)['error'] ?? 'Registration failed.';
    } catch (_) {
      return 'Cannot reach server.';
    }
  }

  static Future<void> logout() async {
    _sessionCookie = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('session');
    await prefs.remove('user_name');
  }
}
