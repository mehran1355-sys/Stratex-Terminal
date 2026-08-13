import 'package:flutter/material.dart';
import 'home_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  final String _fullText = "Smart Technical Risk-managed\nAlgorithmic Trading Executor";
  String _displayedText = "";
  int _charIndex = 0;
  bool _showByLine = false;

  late final AnimationController _fadeController;
  late final Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _startTypewriter();

    _fadeController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeIn,
    );
  }

  void _startTypewriter() {
    Future.delayed(const Duration(milliseconds: 300), () {
      _typeNextChar();
    });
  }

  void _typeNextChar() {
    if (_charIndex < _fullText.length) {
      setState(() {
        _displayedText += _fullText[_charIndex];
        _charIndex++;
      });
      Future.delayed(const Duration(milliseconds: 80), _typeNextChar);
    } else {
      // تایپ تمام شد – by mehran trader را نشان بده
      setState(() {
        _showByLine = true;
      });
      _fadeController.forward();
      // بعد از ۲ ثانیه برو به Home
      Future.delayed(const Duration(seconds: 2), () {
        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (_) => const HomeScreen()),
          );
        }
      });
    }
  }

  @override
  void dispose() {
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundColor,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // متن اصلی با انیمیشن تایپ
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(
                _displayedText,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.accentColor,
                  height: 1.4,
                ),
              ),
            ),
            const SizedBox(height: 24),
            // by mehran trader – با Fade ظاهر می‌شود
            FadeTransition(
              opacity: _fadeAnimation,
              child: _showByLine
                  ? const Text(
                      "by mehran trader",
                      style: TextStyle(
                        fontSize: 16,
                        fontStyle: FontStyle.italic,
                        color: Colors.white70,
                      ),
                    )
                  : const SizedBox.shrink(),
            ),
          ],
        ),
      ),
    );
  }
}
