class SignalModel {
  final String symbol;
  final String timeframe;
  final String direction;
  final String breakType;
  final Map<String, dynamic> entryPlan;
  final double tp1;
  final double tp2;
  final double sl;
  final double volume;
  final String status;
  final String? cancellationReason;
  final DateTime createdAt;

  SignalModel({
    required this.symbol,
    required this.timeframe,
    required this.direction,
    required this.breakType,
    required this.entryPlan,
    required this.tp1,
    required this.tp2,
    required this.sl,
    required this.volume,
    required this.status,
    this.cancellationReason,
    required this.createdAt,
  });

  factory SignalModel.fromJson(Map<String, dynamic> json) {
    return SignalModel(
      symbol: json['symbol'] ?? '',
      timeframe: json['timeframe'] ?? '',
      direction: json['direction'] ?? '',
      breakType: json['break_type'] ?? '',
      entryPlan: json['entry_plan'] ?? {},
      tp1: (json['tp1'] ?? 0).toDouble(),
      tp2: (json['tp2'] ?? 0).toDouble(),
      sl: (json['sl'] ?? 0).toDouble(),
      volume: (json['volume'] ?? 0).toDouble(),
      status: json['status'] ?? '',
      cancellationReason: json['cancellation_reason'],
      createdAt: DateTime.tryParse(json['created_at'] ?? '') ?? DateTime.now(),
    );
  }

  bool get isBullish => direction == 'صعودی';
  String get directionEmoji => isBullish ? '🟢' : '🔴';
  String get directionText => isBullish ? 'خرید' : 'فروش';
  bool get isCompleteBreak => breakType == 'شکست_تکمیلی';
  
  String get formattedEntryZones {
    if (entryPlan.isEmpty) return 'نامشخص';
    List<String> zones = [];
    entryPlan.forEach((zone, entries) {
      if (entries is List && entries.isNotEmpty) {
        String zoneName = zone == 'middle' ? 'میانی' : 'دور';
        List<String> prices = entries.map<String>((e) => e['price'].toStringAsFixed(4)).toList();
        zones.add('$zoneName: ${prices.join(" | ")}');
      }
    });
    return zones.join('\n');
  }
}
