import 'package:flutter/material.dart';
import '../models/backtest_model.dart';

class BacktestResultCard extends StatelessWidget {
  final BacktestResultModel result;
  const BacktestResultCard({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final overview = result.summary['overview'] ?? {};
    final performance = result.summary['performance'] ?? {};

    return Column(children: [
      Card(
        color: AppTheme.surfaceColor,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('📊 خلاصه', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const Divider(),
            _row('بازه', overview['period'] ?? '-'),
            _row('موجودی نهایی', overview['final_balance'] ?? '-'),
            _row('بازده کل', overview['total_return'] ?? '0%', bold: true),
          ]),
        ),
      ),
      const SizedBox(height: 8),
      Card(
        color: AppTheme.surfaceColor,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('📈 عملکرد', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
            const Divider(),
            Row(children: [
              _statBox('کل معاملات', '${performance['total_trades'] ?? 0}', Colors.white),
              _statBox('برد', '${performance['winning_trades'] ?? 0}', AppTheme.successColor),
              _statBox('باخت', '${performance['losing_trades'] ?? 0}', AppTheme.dangerColor),
            ]),
            const SizedBox(height: 8),
            _row('Win Rate', performance['win_rate'] ?? '0%'),
            _row('Profit Factor', performance['profit_factor'] ?? '0'),
            _row('Max Drawdown', performance['max_drawdown'] ?? '0'),
          ]),
        ),
      ),
    ]);
  }

  Widget _row(String label, String value, {bool bold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
        Text(label, style: TextStyle(color: Colors.grey[400], fontSize: 13)),
        Text(value, style: TextStyle(fontWeight: bold ? FontWeight.bold : FontWeight.normal, fontSize: 14)),
      ]),
    );
  }

  Widget _statBox(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(8),
        margin: const EdgeInsets.all(2),
        decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(6)),
        child: Column(children: [
          Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: color)),
          Text(label, style: TextStyle(fontSize: 9, color: Colors.grey[400])),
        ]),
      ),
    );
  }
}
