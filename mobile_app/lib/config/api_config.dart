class ApiConfig {
  static String baseUrl = 'http://192.168.1.100:8000';
  
  static const String healthCheck = '/health';
  static const String symbolsList = '/api/symbols/list';
  static const String symbolsAdd = '/api/symbols/add';
  static const String analysisRun = '/api/analysis/run';
  static const String analysisBatch = '/api/analysis/batch';
  static const String tradesActive = '/api/trades/active';
  static const String tradesHistory = '/api/trades/history';
  static const String reportsDaily = '/api/reports/daily';
  static const String lotSettings = '/api/lot/settings';
  static const String lotSet = '/api/lot/set';
  static const String marketStatus = '/api/market/status';
  static const String marketSelect = '/api/market/select';
  static const String marketStyle = '/api/market/style';
  static const String backtestRun = '/api/backtest/run';
  static const String backtestTimeframes = '/api/backtest/timeframes';
  
  static const int connectionTimeout = 10;
}
