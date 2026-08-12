import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/signal_provider.dart';
import '../widgets/signal_card.dart';

class SignalsScreen extends StatelessWidget {
  const SignalsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📡 سیگنال‌ها'),
        actions: [IconButton(onPressed: () => context.read<SignalProvider>().clearSignals(), icon: const Icon(Icons.clear_all))],
      ),
      body: Consumer<SignalProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading) return const Center(child: CircularProgressIndicator());
          if (provider.signals.isEmpty) {
            return Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.notifications_off, size: 64, color: Colors.grey[600]), const SizedBox(height: 16), Text('هیچ سیگنالی نیست', style: TextStyle(fontSize: 16, color: Colors.grey[600]))]));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: provider.signals.length,
            itemBuilder: (context, index) => SignalCard(signal: provider.signals[index]),
          );
        },
      ),
    );
  }
}
