import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  Map<String, String> get _headers => {'Content-Type': 'application/json'};

  Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.healthCheck}')).timeout(Duration(seconds: ApiConfig.connectionTimeout));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<List<String>> getSymbols() async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.symbolsList}'), headers: _headers);
      if (response.statusCode == 200) {
        return List<String>.from(json.decode(response.body)['symbols'] ?? []);
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  Future<bool> addSymbol(String symbol) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.symbolsAdd}'), headers: _headers, body: json.encode({'symbols': [symbol], 'timeframes': ['monthly', 'weekly', 'daily']}));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> runAnalysis({required String symbol, required String timeframe, double volume = 0.01}) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.analysisRun}'), headers: _headers, body: json.encode({'symbol': symbol, 'timeframe': timeframe, 'volume': volume}));
      if (response.statusCode == 200) return json.decode(response.body);
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> runBatchAnalysis(List<String> symbols) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.analysisBatch}'), headers: _headers, body: json.encode({'symbols': symbols, 'timeframes': ['monthly', 'weekly', 'daily']}));
      if (response.statusCode == 200) return json.decode(response.body);
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<List<dynamic>> getActiveTrades() async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.tradesActive}'), headers: _headers);
      if (response.statusCode == 200) return json.decode(response.body)['active_trades'] ?? [];
      return [];
    } catch (_) {
      return [];
    }
  }

  Future<Map<String, dynamic>?> getLotSettings() async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.lotSettings}'), headers: _headers);
      return response.statusCode == 200 ? json.decode(response.body) : null;
    } catch (_) {
      return null;
    }
  }

  Future<bool> setLotSettings(String assetType, double lot) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.lotSet}'), headers: _headers, body: json.encode({'asset_type': assetType, 'default_lot': lot}));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> getMarketStatus() async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.marketStatus}'), headers: _headers);
      return response.statusCode == 200 ? json.decode(response.body) : null;
    } catch (_) {
      return null;
    }
  }

  Future<bool> selectMarket(String userId, String market) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.marketSelect}'), headers: _headers, body: json.encode({'user_id': userId, 'market': market}));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<bool> selectStyle(String userId, String style) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.marketStyle}'), headers: _headers, body: json.encode({'user_id': userId, 'style': style}));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<Map<String, dynamic>?> runBacktest(Map<String, dynamic> config) async {
    try {
      final response = await http.post(Uri.parse('${ApiConfig.baseUrl}${ApiConfig.backtestRun}'), headers: _headers, body: json.encode(config));
      if (response.statusCode == 200) return json.decode(response.body);
      return null;
    } catch (_) {
      return null;
    }
  }

  Future<Map<String, dynamic>?> get(String endpoint) async {
    try {
      final response = await http.get(Uri.parse('${ApiConfig.baseUrl}/$endpoint'), headers: _headers);
      return response.statusCode == 200 ? json.decode(response.body) : null;
    } catch (_) {
      return null;
    }
  }
}
