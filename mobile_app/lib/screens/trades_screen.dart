import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/trade_provider.dart';

class TradesScreen extends StatefulWidget {
  const TradesScreen({super.key});
  @override
  State<TradesScreen> createState() => _TradesScreenState();
}

class _TradesScreenState extends State<TradesScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => context.read<TradeProvider>().loadActiveTrades());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('💼 معاملات')),
      body: Consumer<TradeProvider>(
        builder: (context, provider, _) {
          if (provider.isLoading) return const Center(child: CircularProgressIndicator());
          if (provider.activeTrades.isEmpty) return Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.hourglass_empty, size: 64, color: Colors.grey[600]), const SizedBox(height: 16), const Text('هیچ معامله فعالی نیست')]));
          return ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: provider.activeTrades.length,
            itemBuilder: (context, index) {
              final t = provider.activeTrades[index];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(children: [
                    Container(width: 4, height: 60, decoration: BoxDecoration(color: AppTheme.successColor, borderRadius: BorderRadius.circular(2))),
                    const SizedBox(width: 12),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(t['symbol'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontFamily: 'monospace')), Text('تیکت: ${t['ticket'] ?? ''}', style: TextStyle(fontSize: 11, color: Colors.grey[500]))])),
                    Column(crossAxisAlignment: CrossAxisAlignment.end, children: [Text('${t['volume'] ?? 0} لات', style: const TextStyle(fontWeight: FontWeight.bold)), Text(t['type'] ?? '', style: TextStyle(fontSize: 11, color: (t['type'] ?? '').contains('BUY') ? AppTheme.successColor : AppTheme.dangerColor))]),
                  ]),
                ),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(onPressed: () => context.read<TradeProvider>().loadActiveTrades(), child: const Icon(Icons.refresh)),
    );
  }
}
