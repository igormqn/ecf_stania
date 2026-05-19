import 'package:flutter/material.dart';
import '../main.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

class SignupScreen extends StatefulWidget {
  const SignupScreen({super.key});
  @override
  State<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends State<SignupScreen> {
  final _firstCtrl  = TextEditingController();
  final _lastCtrl   = TextEditingController();
  final _emailCtrl  = TextEditingController();
  final _pwdCtrl    = TextEditingController();
  final _pwd2Ctrl   = TextEditingController();
  bool _loading     = false;
  String? _error;
  bool _obscurePwd  = true;
  bool _obscurePwd2 = true;

  @override
  void dispose() {
    _firstCtrl.dispose(); _lastCtrl.dispose();
    _emailCtrl.dispose(); _pwdCtrl.dispose(); _pwd2Ctrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final first = _firstCtrl.text.trim();
    final last  = _lastCtrl.text.trim();
    final email = _emailCtrl.text.trim();
    final pwd   = _pwdCtrl.text;
    final pwd2  = _pwd2Ctrl.text;

    if (first.isEmpty || last.isEmpty || email.isEmpty || pwd.isEmpty) {
      setState(() => _error = 'All fields are required.');
      return;
    }
    if (pwd != pwd2) {
      setState(() => _error = 'Passwords do not match.');
      return;
    }
    if (pwd.length < 8) {
      setState(() => _error = 'Password must be at least 8 characters.');
      return;
    }

    setState(() { _loading = true; _error = null; });
    final err = await ApiService.signup(
      email: email, password: pwd,
      firstName: first, lastName: last,
    );
    setState(() => _loading = false);

    if (err == null && mounted) {
      Navigator.pushReplacement(
          context, MaterialPageRoute(builder: (_) => const HomeScreen()));
    } else {
      setState(() => _error = err);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: kNavy900,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(28),
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
                    fontSize: 34,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 4,
                  ),
                ),
              ),
              const SizedBox(height: 6),
              const Text('Official Super Bowl Betting',
                  style: TextStyle(color: kTextSecondary, fontSize: 12, letterSpacing: 1)),
              const SizedBox(height: 36),

              Container(
                padding: const EdgeInsets.all(28),
                decoration: BoxDecoration(
                  color: kSurface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: kBorder),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Create Account',
                        style: TextStyle(
                            color: kTextPrimary,
                            fontSize: 22,
                            fontWeight: FontWeight.w800)),
                    const SizedBox(height: 4),
                    const Text('Fill in the form to get started',
                        style: TextStyle(color: kTextSecondary, fontSize: 13)),
                    const SizedBox(height: 24),

                    Row(
                      children: [
                        Expanded(child: _field(_firstCtrl, 'First name', Icons.person_outline)),
                        const SizedBox(width: 12),
                        Expanded(child: _field(_lastCtrl, 'Last name', Icons.person_outline)),
                      ],
                    ),
                    const SizedBox(height: 14),
                    _field(_emailCtrl, 'Email', Icons.email_outlined,
                        type: TextInputType.emailAddress),
                    const SizedBox(height: 14),
                    _pwdField(_pwdCtrl, 'Password', _obscurePwd,
                        () => setState(() => _obscurePwd = !_obscurePwd)),
                    const SizedBox(height: 14),
                    _pwdField(_pwd2Ctrl, 'Confirm password', _obscurePwd2,
                        () => setState(() => _obscurePwd2 = !_obscurePwd2),
                        onSubmit: (_) => _submit()),

                    if (_error != null) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        decoration: BoxDecoration(
                          color: kRed.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: kRed.withOpacity(0.4)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline, color: kRed, size: 16),
                            const SizedBox(width: 8),
                            Expanded(child: Text(_error!,
                                style: const TextStyle(color: kRed, fontSize: 13))),
                          ],
                        ),
                      ),
                    ],

                    const SizedBox(height: 24),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _loading ? null : _submit,
                        child: _loading
                            ? const SizedBox(width: 20, height: 20,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2, color: kNavy900))
                            : const Text('Create Account'),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Center(
                      child: GestureDetector(
                        onTap: () => Navigator.pop(context),
                        child: RichText(
                          text: const TextSpan(
                            text: 'Already have an account? ',
                            style: TextStyle(color: kTextSecondary, fontSize: 13),
                            children: [
                              TextSpan(
                                text: 'Sign In',
                                style: TextStyle(
                                    color: kGold400,
                                    fontWeight: FontWeight.w700),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _field(TextEditingController ctrl, String label, IconData icon,
      {TextInputType type = TextInputType.text}) {
    return TextField(
      controller: ctrl,
      keyboardType: type,
      style: const TextStyle(color: kTextPrimary),
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: Icon(icon),
      ),
    );
  }

  Widget _pwdField(TextEditingController ctrl, String label, bool obscure,
      VoidCallback toggle, {ValueChanged<String>? onSubmit}) {
    return TextField(
      controller: ctrl,
      obscureText: obscure,
      onSubmitted: onSubmit,
      style: const TextStyle(color: kTextPrimary),
      decoration: InputDecoration(
        labelText: label,
        prefixIcon: const Icon(Icons.lock_outline),
        suffixIcon: IconButton(
          icon: Icon(obscure ? Icons.visibility_off_outlined : Icons.visibility_outlined,
              color: kTextSecondary),
          onPressed: toggle,
        ),
      ),
    );
  }
}
