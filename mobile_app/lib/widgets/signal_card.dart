import 'package:flutter/material.dart';
import '../models/signal_model.dart';

class SignalCard extends StatelessWidget {
  final SignalModel signal;
  const SignalCard({super.key, required this.signal});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Text(signal.directionEmoji, style: const TextStyle(fontSize: 28)),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(signal.symbol, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, fontFamily: 'monospace')), Text('${signal.timeframe} | ${signal.directionText}', style: TextStyle(color: Colors.grey[400], fontSize: 12))])),
            Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4), decoration: BoxDecoration(color: (signal.isCompleteBreak ? AppTheme.primaryColor : Colors.orange).withOpacity(0.3), borderRadius: BorderRadius.circular(12)), child: Text(signal.isCompleteBreak ? 'تکمیلی' : 'اولیه', style: TextStyle(fontSize: 11, color: signal.isCompleteBreak ? AppTheme.primaryColor : Colors.orange))),
          ]),
          const Divider(height: 24),
          Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: AppTheme.surfaceColor, borderRadius: BorderRadius.circular(8)), child: Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            _priceItem('🎯 TP1', signal.tp1, AppTheme.successColor),
            _priceItem('🎯 TP2', signal.tp2, AppTheme.primaryColor),
            _priceItem('🛑 SL', signal.sl, AppTheme.dangerColor),
          ])),
          const SizedBox(height: 12),
          Text('📍 مناطق ورود:', style: TextStyle(color: Colors.grey[400], fontSize: 12)),
          const SizedBox(height: 4),
          Text(signal.formattedEntryZones, style: const TextStyle(fontSize: 13)),
          const SizedBox(height: 8),
          Text('💰 حجم: ${signal.volume.toStringAsFixed(4)} لات', style: const TextStyle(fontSize: 13)),
        ]),
      ),
    );
  }

  Widget _priceItem(String label, double price, Color color) {
    return Column(children: [Text(label, style: TextStyle(color: color, fontSize: 11)), const SizedBox(height: 4), Text(price.toStringAsFixed(4), style: TextStyle(color: color, fontWeight: FontWeight.bold, fontFamily: 'monospace', fontSize: 16))]);
  }
}
