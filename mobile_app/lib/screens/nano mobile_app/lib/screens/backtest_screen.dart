import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/backtest_model.dart';
import '../widgets/backtest_result_card.dart';

class BacktestScreen extends StatefulWidget {
  const BacktestScreen({super.key});
  @override
  State<BacktestScreen> createState() => _BacktestScreenState();
}

class _BacktestScreenState extends State<BacktestScreen> {
  final ApiService _api = ApiService();
  String _symbol = 'EURUSD';
  String _timeframe = 'daily';
  DateTime _startDate = DateTime(2023, 1, 1);
  DateTime _endDate = DateTime(2024, 1, 1);
  double _balance = 10000;
  double _volume = 0.10;
  int _splitCount = 2;
  bool _isRunning = false;
  BacktestResultModel? _result;

  final List<String> _timeframes = ['monthly', 'weekly', 'daily', '12h', '8h', '6h', '4h', '2h', '1h', '30m', '15m', '10m', '5m', '3m', '2m', '1m'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('📊 بک‌تست')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(children: [
                Row(children: [const Text('نماد: '), Expanded(child: TextField(decoration: const InputDecoration(hintText: 'EURUSD'), style: const TextStyle(fontFamily: 'monospace'), onChanged: (v) => _symbol = v.toUpperCase(), controller: TextEditingController(text: _symbol)))])),
                const SizedBox(height: 8),
                Wrap(spacing: 6, children: _timeframes.map((tf) => ChoiceChip(label: Text(tf), selected: _timeframe == tf, onSelected: (_) => setState(() => _timeframe = tf), selectedColor: AppTheme.accentColor)).toList()),
                const SizedBox(height: 12),
                Row(children: [
                  const Text('از: '), Expanded(child: OutlinedButton(onPressed: () async { final d = await showDatePicker(context: context, initialDate: _startDate, firstDate: DateTime(2010), lastDate: DateTime.now()); if (d != null) setState(() => _startDate = d); }, child: Text(_startDate.toString().split(' ')[0]))),
                  const SizedBox(width: 8),
                  const Text('تا: '), Expanded(child: OutlinedButton(onPressed: () async { final d = await showDatePicker(context: context, initialDate: _endDate, firstDate: DateTime(2010), lastDate: DateTime.now()); if (d != null) setState(() => _endDate = d); }, child: Text(_endDate.toString().split(' ')[0]))),
                ]),
              ]),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(width: double.infinity, height: 50, child: ElevatedButton.icon(onPressed: _isRunning ? null : _run, icon: _isRunning ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.play_arrow), label: Text(_isRunning ? 'در حال اجرا...' : '🚀 اجرای بک‌تست'))),
          const SizedBox(height: 16),
          if (_result != null) BacktestResultCard(result: _result!),
        ]),
      ),
    );
  }

  Future<void> _run() async {
    setState(() => _isRunning = true);
    final model = BacktestModel(symbol: _symbol, timeframe: _timeframe, startDate: _startDate.toIso8601String().split('T')[0], endDate: _endDate.toIso8601String().split('T')[0], initialBalance: _balance, totalVolume: _volume, splitCount: _splitCount);
    final result = await _api.runBacktest(model.toJson());
    setState(() { _isRunning = false; if (result != null) _result = BacktestResultModel.fromJson(result); });
  }
}
