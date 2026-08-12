import 'package:flutter/material.dart';
import '../services/api_service.dart';

class LotSettingsScreen extends StatefulWidget {
  const LotSettingsScreen({super.key});
  @override
  State<LotSettingsScreen> createState() => _LotSettingsScreenState();
}

class _LotSettingsScreenState extends State<LotSettingsScreen> {
  final ApiService _api = ApiService();
  Map<String, double> _lots = {"forex_pairs": 0.10, "commodities": 0.05, "indices": 1.0, "crypto": 0.10, "stocks": 10.0};

  Future<void> _save() async {
    for (final e in _lots.entries) {
      await _api.setLotSettings(e.key, e.value);
    }
    if (mounted) ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('✅ ذخیره شد'), backgroundColor: AppTheme.successColor));
  }

  @override
  Widget build(BuildContext context) {
    final assets = {"forex_pairs": ["💱", "جفت ارزها", 0.01, 50.0], "commodities": ["🥇", "کالاها", 0.01, 20.0], "indices": ["📈", "شاخص‌ها", 0.10, 100.0], "crypto": ["₿", "ارز دیجیتال", 0.01, 10.0], "stocks": ["🏢", "سهام", 1.0, 10000.0]};
    
    return Scaffold(
      appBar: AppBar(title: const Text('💰 تنظیمات لات'), actions: [TextButton(onPressed: _save, child: const Text('💾 ذخیره', style: TextStyle(color: AppTheme.successColor)))]),
      body: ListView(padding: const EdgeInsets.all(16), children: assets.entries.map((e) {
        final info = e.value;
        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [Text(info[0], style: const TextStyle(fontSize: 24)), const SizedBox(width: 12), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(info[1], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)), Text('حداقل: ${info[2]} | حداکثر: ${info[3]}', style: TextStyle(fontSize: 11, color: Colors.grey[500]))])), Text(_lots[e.key]!.toStringAsFixed(2), style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.accentColor))]),
              const SizedBox(height: 12),
              Slider(value: _lots[e.key]!, min: info[2] as double, max: info[3] as double, activeColor: AppTheme.accentColor, onChanged: (v) => setState(() => _lots[e.key] = double.parse(v.toStringAsFixed(2)))),
            ]),
          ),
        );
      }).toList()),
    );
  }
}
