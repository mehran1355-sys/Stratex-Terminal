import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../config/api_config.dart';
import 'lot_settings_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});
  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final TextEditingController _serverController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _serverController.text = ApiConfig.baseUrl;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('⚙️ تنظیمات')),
      body: Consumer<SettingsProvider>(
        builder: (context, settings, _) {
          return ListView(padding: const EdgeInsets.all(16), children: [
            _sectionHeader('🔗 اتصال'),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(children: [
                  TextField(controller: _serverController, decoration: const InputDecoration(labelText: 'آدرس سرور', prefixIcon: Icon(Icons.link)), onChanged: (v) { ApiConfig.baseUrl = v; settings.updateServerUrl(v); }),
                  const SizedBox(height: 8),
                  Row(children: [Icon(Icons.circle, size: 10, color: settings.isConnected ? Colors.green : Colors.red), const SizedBox(width: 8), Text(settings.isConnected ? 'متصل' : 'قطع', style: TextStyle(color: settings.isConnected ? Colors.green : Colors.red))]),
                ]),
              ),
            ),
            const SizedBox(height: 16),
            _sectionHeader('💰 لات'),
            Card(child: ListTile(leading: const Icon(Icons.tune, color: AppTheme.accentColor), title: const Text('مدیریت لات'), trailing: const Icon(Icons.chevron_left), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const LotSettingsScreen())))),
            const SizedBox(height: 16),
            _sectionHeader('🛡️ ریسک'),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(children: [
                  _slider('حداکثر ریسک پرتفوی', settings.maxPortfolioRisk * 100, 10, 100, (v) => settings.setMaxPortfolioRisk(v / 100), '%'),
                  const SizedBox(height: 8),
                  _slider('حداکثر ریسک هر معامله', settings.maxRiskPerTrade * 100, 1, 10, (v) => settings.setMaxRiskPerTrade(v / 100), '%'),
                ]),
              ),
            ),
          ]);
        },
      ),
    );
  }

  Widget _sectionHeader(String title) => Padding(padding: const EdgeInsets.only(bottom: 8), child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.accentColor)));
  
  Widget _slider(String title, double value, double min, double max, Function(double) onChanged, String unit) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(title, style: const TextStyle(fontSize: 14)), Text('${value.toStringAsFixed(0)}$unit', style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.accentColor))]),
      Slider(value: value, min: min, max: max, divisions: ((max - min) / 5).round(), activeColor: AppTheme.accentColor, onChanged: onChanged),
    ]);
  }
}
