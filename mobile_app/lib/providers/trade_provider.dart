import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class TradeProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  List<Map<String, dynamic>> _activeTrades = [];
  List<Map<String, dynamic>> get activeTrades => _activeTrades;
  bool _isLoading = false;
  bool get isLoading => _isLoading;

  Future<void> loadActiveTrades() async {
    _isLoading = true;
    notifyListeners();
    _activeTrades = await _api.getActiveTrades();
    _isLoading = false;
    notifyListeners();
  }

  int get activeTradesCount => _activeTrades.length;
}
