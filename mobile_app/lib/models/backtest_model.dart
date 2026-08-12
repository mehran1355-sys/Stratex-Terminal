class BacktestModel {
  final String symbol;
  final String timeframe;
  final String startDate;
  final String endDate;
  final double initialBalance;
  final double totalVolume;
  final int splitCount;
  final bool enableTP1Partial;
  final bool useRiskManagement;
  final double maxRiskPct;
  final double spreadPips;

  BacktestModel({
    required this.symbol,
    required this.timeframe,
    required this.startDate,
    required this.endDate,
    this.initialBalance = 10000,
    this.totalVolume = 0.10,
    this.splitCount = 2,
    this.enableTP1Partial = true,
    this.useRiskManagement = true,
    this.maxRiskPct = 2.0,
    this.spreadPips = 1.0,
  });

  Map<String, dynamic> toJson() => {
    'symbol': symbol,
    'timeframe': timeframe,
    'start_date': startDate,
    'end_date': endDate,
    'initial_balance': initialBalance,
    'total_volume': totalVolume,
    'split_count': splitCount,
    'enable_tp1_partial': enableTP1Partial,
    'use_risk_management': useRiskManagement,
    'max_risk_pct': maxRiskPct,
    'spread_pips': spreadPips,
  };
}

class BacktestResultModel {
  final Map<String, dynamic> summary;
  final List<Map<String, dynamic>> monthlyAnalysis;
  final Map<String, dynamic> streaks;
  final int tradesCount;

  BacktestResultModel({
    required this.summary,
    required this.monthlyAnalysis,
    required this.streaks,
    required this.tradesCount,
  });

  factory BacktestResultModel.fromJson(Map<String, dynamic> json) {
    return BacktestResultModel(
      summary: json['summary'] ?? {},
      monthlyAnalysis: List<Map<String, dynamic>>.from(json['monthly_analysis'] ?? []),
      streaks: json['streaks'] ?? {},
      tradesCount: json['trades_count'] ?? 0,
    );
  }
}
