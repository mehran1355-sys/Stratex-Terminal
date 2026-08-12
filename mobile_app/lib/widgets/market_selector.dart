import 'package:flutter/material.dart';
import '../services/api_service.dart';

class MarketSelectorWidget extends StatefulWidget {
  const MarketSelectorWidget({super.key});
  @override
  State<MarketSelectorWidget> createState() => _MarketSelectorWidgetState();
}

class _MarketSelectorWidgetState extends State<MarketSelectorWidget> {
  String _selected = 'forex';

  @override
  Widget build(BuildContext context) {
    final markets = {"forex": ["💱", "فارکس", true], "stocks": ["📈", "سهام", false], "crypto": ["₿", "کریپتو", false], "iran_stocks": ["🇮🇷", "ایران", false]};
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('انتخاب بازار', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: markets.entries.map((e) {
            final isSel = _selected == e.key;
            final avail = e.value[2] as bool;
            return Padding(
              padding: const EdgeInsets.only(right: 8),
              child: InkWell(
                onTap: avail ? () async { await ApiService().selectMarket('default', e.key); setState(() => _selected = e.key); } : null,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(color: isSel ? AppTheme.primaryColor : AppTheme.surfaceColor, borderRadius: BorderRadius.circular(8), border: Border.all(color: isSel ? AppTheme.accentColor : Colors.white24)),
                  child: Column(children: [Text(e.value[0] as String, style: const TextStyle(fontSize: 24)), const SizedBox(height: 4), Text(e.value[1] as String, style: TextStyle(color: isSel ? Colors.white : Colors.grey)), if (!avail) const Text('به زودی', style: TextStyle(fontSize: 9, color: Colors.orange))]),
                ),
              ),
            );
          }).toList())),
        ]),
      ),
    );
  }
}
