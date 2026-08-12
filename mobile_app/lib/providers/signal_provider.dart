import 'package:flutter/foundation.dart';
import '../models/signal_model.dart';
import '../services/api_service.dart';

class SignalProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  List<SignalModel> _signals = [];
  List<SignalModel> get signals => _signals;
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  Future<void> runAnalysis(String symbol, String timeframe) async {
    _isLoading = true;
    notifyListeners();
    final result = await _api.runAnalysis(symbol: symbol, timeframe: timeframe);
    if (result != null && result['success'] == true) {
      final signalData = result['signal'] as Map<String, dynamic>?;
      if (signalData != null) {
        _signals.insert(0, SignalModel.fromJson({
          ...signalData,
          'symbol': symbol,
          'timeframe': timeframe,
          'created_at': DateTime.now().toIso8601String(),
        }));
      }
    }
    _isLoading = false;
    notifyListeners();
  }

  void clearSignals() { _signals.clear(); notifyListeners(); }
}
