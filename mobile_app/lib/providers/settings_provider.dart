import 'package:flutter/foundation.dart';
import '../services/api_service.dart';
import '../config/api_config.dart';

class SettingsProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  
  bool _isConnected = false;
  bool get isConnected => _isConnected;

  double _maxPortfolioRisk = 0.40;
  double get maxPortfolioRisk => _maxPortfolioRisk;

  double _maxRiskPerTrade = 0.02;
  double get maxRiskPerTrade => _maxRiskPerTrade;

  bool _askUserOnLimitExceeded = true;
  bool get askUserOnLimitExceeded => _askUserOnLimitExceeded;

  String _executionMode = 'semi_auto';
  String get executionMode => _executionMode;

  double _currentMarginUsed = 0;
  double get currentMarginUsed => _currentMarginUsed;

  double _accountBalance = 10000;
  double get accountBalance => _accountBalance;

  Future<bool> checkConnection() async {
    _isConnected = await _api.checkHealth();
    notifyListeners();
    return _isConnected;
  }

  void updateServerUrl(String url) {
    ApiConfig.baseUrl = url;
    checkConnection();
  }

  void setMaxPortfolioRisk(double value) { _maxPortfolioRisk = value; notifyListeners(); }
  void setMaxRiskPerTrade(double value) { _maxRiskPerTrade = value; notifyListeners(); }
  void setAskUserOnLimit(bool value) { _askUserOnLimitExceeded = value; notifyListeners(); }
  void setExecutionMode(String mode) { _executionMode = mode; notifyListeners(); }
}
