import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/signal_model.dart';
import '../providers/signal_provider.dart';
import '../services/api_service.dart';
import '../widgets/signal_card.dart';

class AnalysisScreen extends StatefulWidget {
  const AnalysisScreen({super.key});
  @override
  State<AnalysisScreen> createState() => _AnalysisScreenState();
}

class _AnalysisScreenState extends State<AnalysisScreen> {
  final ApiService _api = ApiService();
  List<String> _symbols = [];
  String? _selectedSymbol;
  String _selectedTimeframe = 'daily';
  bool _isAnalyzing = false;
  SignalModel? _lastSignal;
  String? _errorMessage;

  final Map<String, String> _timeframes = {
    'monthly': 'ماهیانه', 'weekly': 'هفتگی', 'daily': 'روزانه',
    '12h': '۱۲ ساعته', '8h': '۸ ساعته', '6h': '۶ ساعته', '4h': '۴ ساعته', '2h': '۲ ساعته', '1h': '۱ ساعته',
    '30m': '۳۰ دقیقه', '15m': '۱۵ دقیقه', '10m': '۱۰ دقیقه', '5m': '۵ دقیقه', '3m': '۳ دقیقه', '2m': '۲ دقیقه', '1m': '۱ دقیقه',
  };

  final TextEditingController _symbolController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadSymbols();
  }

  Future<void> _loadSymbols() async {
    final symbols = await _api.getSymbols();
    setState(() {
      _symbols = symbols;
      if (symbols.isNotEmpty) _selectedSymbol = symbols.first;
    });
  }

  Future<void> _runAnalysis() async {
    if (_selectedSymbol == null) {
      setState(() => _errorMessage = 'لطفاً یک نماد انتخاب کنید');
      return;
    }
    setState(() { _isAnalyzing = true; _errorMessage = null; _lastSignal = null; });
    final result = await _api.runAnalysis(symbol: _selectedSymbol!, timeframe: _selectedTimeframe);
    setState(() {
      _isAnalyzing = false;
      if (result != null && result['success'] == true) {
        final signalData = result['signal'] as Map<String, dynamic>?;
        if (signalData != null) {
          _lastSignal = SignalModel.fromJson({
            ...signalData,
            'symbol': _selectedSymbol,
            'timeframe': _selectedTimeframe,
            'created_at': DateTime.now().toIso8601String(),
          });
        } else {
          _errorMessage = 'سیگنالی یافت نشد';
        }
      } else {
        _errorMessage = result?['message'] ?? 'خطا در تحلیل';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🔍 تحلیل'), actions: [IconButton(onPressed: _loadSymbols, icon: const Icon(Icons.refresh))]),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('انتخاب نماد', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                if (_symbols.isNotEmpty)
                  DropdownButtonFormField<String>(
                    value: _selectedSymbol,
                    items: _symbols.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(fontFamily: 'monospace')))).toList(),
                    onChanged: (v) => setState(() => _selectedSymbol = v),
                    decoration: const InputDecoration(prefixIcon: Icon(Icons.search)),
                  ),
                const SizedBox(height: 8),
                Row(children: [
                  Expanded(child: TextField(controller: _symbolController, decoration: const InputDecoration(hintText: 'افزودن نماد...', prefixIcon: Icon(Icons.add)), style: const TextStyle(fontFamily: 'monospace'))),
                  const SizedBox(width: 8),
                  ElevatedButton(onPressed: () async {
                    final s = _symbolController.text.trim().toUpperCase();
                    if (s.isNotEmpty) { await _api.addSymbol(s); _symbolController.clear(); _loadSymbols(); }
                  }, child: const Text('➕')),
                ]),
              ]),
            ),
          ),
          const SizedBox(height: 12),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('تایم‌فریم', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Wrap(spacing: 8, children: _timeframes.entries.map((e) {
                  final isSelected = _selectedTimeframe == e.key;
                  final isNew = ['12h','8h','6h','2h','10m','3m','2m'].contains(e.key);
                  return ChoiceChip(
                    label: Row(mainAxisSize: MainAxisSize.min, children: [Text(e.value), if (isNew) const Text(' جدید', style: TextStyle(fontSize: 8, color: Colors.green))]),
                    selected: isSelected,
                    onSelected: (_) => setState(() => _selectedTimeframe = e.key),
                    selectedColor: AppTheme.accentColor,
                  );
                }).toList()),
              ]),
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(width: double.infinity, height: 50, child: ElevatedButton.icon(onPressed: _isAnalyzing ? null : _runAnalysis, icon: const Icon(Icons.analytics), label: Text(_isAnalyzing ? 'در حال تحلیل...' : '🔍 تحلیل ${_selectedSymbol ?? ""}'))),
          const SizedBox(height: 16),
          if (_isAnalyzing) const Center(child: CircularProgressIndicator()),
          if (_errorMessage != null) Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(color: AppTheme.dangerColor.withOpacity(0.1), borderRadius: BorderRadius.circular(8)), child: Row(children: [const Icon(Icons.error, color: AppTheme.dangerColor), const SizedBox(width: 8), Expanded(child: Text(_errorMessage!, style: const TextStyle(color: AppTheme.dangerColor)))])),
          if (_lastSignal != null) ...[const SizedBox(height: 16), SignalCard(signal: _lastSignal!)],
        ]),
      ),
    );
  }
}
