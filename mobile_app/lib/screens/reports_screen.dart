import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});
  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  final ApiService _api = ApiService();
  Map<String, dynamic>? _dailyReport;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadReports();
  }

  Future<void> _loadReports() async {
    setState(() => _isLoading = true);
    try {
      final response = await _api.get('api/reports/daily');
      _dailyReport = response;
    } catch (_) {}
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('📊 گزارشات')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadReports,
              child: ListView(padding: const EdgeInsets.all(16), children: [
                _buildReportCard('📅 گزارش روزانه', _dailyReport),
              ]),
            ),
    );
  }

  Widget _buildReportCard(String title, Map<String, dynamic>? data) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [const Icon(Icons.today, color: AppTheme.accentColor), const SizedBox(width: 8), Text(title, style: const TextStyle(fontWeight: FontWeight.bold))]),
          const SizedBox(height: 12),
          if (data != null && data['statistics'] != null)
            Column(children: [
              _statRow('معاملات فعال', '${data['statistics']['active_trades'] ?? 0}'),
              _statRow('کل امروز', '${data['statistics']['total_trades_today'] ?? 0}'),
              _statRow('سود/ضرر', '\$${(data['statistics']['daily_pnl'] ?? 0).toStringAsFixed(2)}'),
            ])
          else
            const Text('داده‌ای موجود نیست', style: TextStyle(color: Colors.grey)),
        ]),
      ),
    );
  }

  Widget _statRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Text(label, style: TextStyle(color: Colors.grey[400])),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
      ]),
    );
  }
}
