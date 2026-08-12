import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'app.dart';
import 'providers/settings_provider.dart';
import 'providers/signal_provider.dart';
import 'providers/trade_provider.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ChangeNotifierProvider(create: (_) => SignalProvider()),
        ChangeNotifierProvider(create: (_) => TradeProvider()),
      ],
      child: const SupplyDemandApp(),
    ),
  );
}
