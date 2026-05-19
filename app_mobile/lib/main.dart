import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

// ── Palette identique au site web ──────────────────────────────────────────
const kNavy900  = Color(0xFF080F1E);
const kNavy800  = Color(0xFF0D1729);
const kNavy700  = Color(0xFF112035);
const kNavy600  = Color(0xFF162840);
const kGold500  = Color(0xFFF59E0B);
const kGold400  = Color(0xFFFBBF24);
const kCyan400  = Color(0xFF22D3EE);
const kTextPrimary   = Color(0xFFF1F5F9);
const kTextSecondary = Color(0xFF94A3B8);
const kSurface  = Color(0xFF111827);
const kBorder   = Color(0xFF1F2937);
const kGreen    = Color(0xFF4ADE80);
const kRed      = Color(0xFFF87171);
const kOrange   = Color(0xFFFB923C);

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(const StaniaBetApp());
}

class StaniaBetApp extends StatelessWidget {
  const StaniaBetApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Stania Bet',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: kNavy900,
        colorScheme: const ColorScheme.dark(
          primary: kGold500,
          secondary: kCyan400,
          surface: kSurface,
          error: kRed,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: kNavy800,
          elevation: 0,
          titleTextStyle: TextStyle(
            color: kTextPrimary,
            fontSize: 17,
            fontWeight: FontWeight.w700,
            letterSpacing: 0.3,
          ),
          iconTheme: IconThemeData(color: kTextPrimary),
          surfaceTintColor: Colors.transparent,
        ),
        cardTheme: CardThemeData(
          color: kSurface,
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: kBorder),
          ),
          margin: const EdgeInsets.symmetric(vertical: 6),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: kNavy700,
          labelStyle: const TextStyle(color: kTextSecondary),
          hintStyle: const TextStyle(color: kTextSecondary),
          prefixIconColor: kTextSecondary,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: kBorder),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: kBorder),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
            borderSide: const BorderSide(color: kGold500, width: 2),
          ),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: kGold500,
            foregroundColor: kNavy900,
            textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
            padding: const EdgeInsets.symmetric(vertical: 15),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            elevation: 0,
          ),
        ),
        dividerTheme: const DividerThemeData(color: kBorder, thickness: 1),
        textTheme: const TextTheme(
          bodyLarge:  TextStyle(color: kTextPrimary),
          bodyMedium: TextStyle(color: kTextSecondary),
          titleLarge: TextStyle(color: kTextPrimary, fontWeight: FontWeight.bold),
        ),
        fontFamily: 'Inter',
        useMaterial3: true,
      ),
      home: const _Splash(),
      routes: {
        '/login': (_) => const LoginScreen(),
        '/home':  (_) => const HomeScreen(),
      },
    );
  }
}

class _Splash extends StatefulWidget {
  const _Splash();
  @override
  State<_Splash> createState() => _SplashState();
}

class _SplashState extends State<_Splash> {
  @override
  void initState() {
    super.initState();
    _check();
  }

  Future<void> _check() async {
    final prefs = await SharedPreferences.getInstance();
    final session = prefs.getString('session');
    if (!mounted) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (_) => (session != null && session.isNotEmpty)
            ? const HomeScreen()
            : const LoginScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kNavy900,
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ShaderMask(
              shaderCallback: (b) => const LinearGradient(
                colors: [kGold400, kCyan400],
              ).createShader(b),
              child: const Text(
                'STANIA BET',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 36,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 4,
                ),
              ),
            ),
            const SizedBox(height: 8),
            const Text('Official Super Bowl Betting',
                style: TextStyle(color: kTextSecondary, fontSize: 13, letterSpacing: 1)),
            const SizedBox(height: 48),
            const SizedBox(
              width: 28, height: 28,
              child: CircularProgressIndicator(
                color: kGold500, strokeWidth: 2.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
