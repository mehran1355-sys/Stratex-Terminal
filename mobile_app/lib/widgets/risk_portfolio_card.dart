import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';

class RiskPortfolioCard extends StatelessWidget {
  const RiskPortfolioCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<SettingsProvider>(
      builder: (context, settings, _) {
        final maxPct = settings.maxPortfolioRisk * 100;
        return Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                Container(padding: const EdgeInsets.all(8), decoration: BoxDecoration(color: AppTheme.dangerColor.withOpacity(0.2), borderRadius: BorderRadius.circular(8)), child: const Icon(Icons.shield, color: AppTheme.dangerColor, size: 22)),
                const SizedBox(width: 12),
                const Expanded(child: Text('🛡️ مدیریت ریسک کل', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15))),
                Text('${maxPct.toStringAsFixed(0)}%', style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.accentColor, fontSize: 18)),
              ]),
              const SizedBox(height: 12),
              ClipRRect(borderRadius: BorderRadius.circular(4), child: LinearProgressIndicator(value: 0.25, backgroundColor: Colors.grey[800], valueColor: const AlwaysStoppedAnimation(AppTheme.successColor), minHeight: 8)),
              const SizedBox(height: 8),
              Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('درگیر: ۲۵٪', style: TextStyle(fontSize: 12, color: AppTheme.successColor)), Text('مجاز: ${maxPct.toStringAsFixed(0)}%', style: const TextStyle(fontSize: 12, color: Colors.grey))]),
              const Text('✅ ۱۵٪ ظرفیت باقی‌مانده', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppTheme.successColor)),
            ]),
          ),
        );
      },
    );
  }
}
