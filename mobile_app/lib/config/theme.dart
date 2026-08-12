import 'package:flutter/material.dart';

class AppTheme {
  static const Color primaryColor = Color(0xFF2F5496);
  static const Color accentColor = Color(0xFFFF8C00);
  static const Color successColor = Color(0xFF00C853);
  static const Color dangerColor = Color(0xFFFF1744);
  static const Color backgroundColor = Color(0xFF1a1a2e);
  static const Color surfaceColor = Color(0xFF16213e);
  static const Color cardColor = Color(0xFF0f3460);

  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      primaryColor: primaryColor,
      scaffoldBackgroundColor: backgroundColor,
      appBarTheme: const AppBarTheme(
        backgroundColor: surfaceColor,
        elevation: 0,
        centerTitle: true,
      ),
      cardTheme: CardTheme(
        color: cardColor,
        elevation: 4,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
    );
  }
}
