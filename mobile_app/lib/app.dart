import 'package:flutter/material.dart';
import 'config/theme.dart';
import 'screens/home_screen.dart';

class SupplyDemandApp extends StatelessWidget {
  const SupplyDemandApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
  title: 'Stratex Terminal',
  ...
);
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const HomeScreen(),
    );
  }
}
