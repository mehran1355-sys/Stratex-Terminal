import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../services/api_service.dart';
import '../widgets/market_selector.dart';
import '../widgets/style_selector.dart';
import '../widgets/risk_portfolio_card.dart';
import 'analysis_screen.dart';
import 'signals_screen.dart';
import 'trades_screen.dart';
import 'settings_screen.dart';
import 'backtest_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isConnected = false;
  int _activeTrades = 0;

  @override
  void initState() {
    super.initState();
    _checkConnection();
  }

  Future<void> _checkConnection() async {
    final connected = await ApiService().checkHealth();
    setState(() => _isConnected = connected);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📊 Supply & Demand'),
        actions: [
          Container(
            margin: const EdgeInsets.only(right: 12),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.circle, size: 10, color: _isConnected ? Colors.green : Colors.red),
              const SizedBox(width: 4),
              Text(_isConnected ? 'متصل' : 'قطع', style: TextStyle(fontSize: 12, color: _isConnected ? Colors.green : Colors.red)),
            ]),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          _buildMarketCard(),
          const SizedBox(height: 16),
          _buildSummaryCards(),
          const SizedBox(height: 16),
          const MarketSelectorWidget(),
          const SizedBox(height: 12),
          const StyleSelectorWidget(),
          const SizedBox(height: 16),
          const RiskPortfolioCard(),
          const SizedBox(height: 20),
          _buildMainButtons(),
        ]),
      ),
    );
  }

  Widget _buildMarketCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [const Icon(Icons.radar, color: AppTheme.accentColor), const SizedBox(width: 8), Text('وضعیت بازار', style: Theme.of(context).textTheme.titleMedium)]),
          const SizedBox(height: 12),
          Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
            _buildMarketStatus('فارکس', true),
            _buildMarketStatus('سهام', false),
            _buildMarketStatus('کریپتو', false),
            _buildMarketStatus('ایران', false),
          ]),
        ]),
      ),
    );
  }

  Widget _buildMarketStatus(String name, bool isActive) {
    return Column(children: [
      Icon(isActive ? Icons.check_circle : Icons.schedule, color: isActive ? AppTheme.successColor : Colors.grey, size: 28),
      const SizedBox(height: 4),
      Text(name, style: TextStyle(fontSize: 12, color: isActive ? Colors.white : Colors.grey)),
    ]);
  }

  Widget _buildSummaryCards() {
    return Row(children: [
      Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Text('$_activeTrades', style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppTheme.accentColor)), const Text('معامله فعال')])))),
      const SizedBox(width: 12),
      Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [const Text('0', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppTheme.successColor)), const Text('سیگنال امروز')])))),
    ]);
  }

  Widget _buildMainButtons() {
    return Column(children: [
      _buildButton('🔍 اجرای تحلیل جدید', Icons.analytics, () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AnalysisScreen()))),
      const SizedBox(height: 8),
      _buildButton('📡 مشاهده سیگنال‌ها', Icons.notifications_active, () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SignalsScreen()))),
      const SizedBox(height: 8),
      _buildButton('💼 معاملات فعال', Icons.swap_horiz, () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TradesScreen()))),
      const SizedBox(height: 8),
      _buildButton('📊 بک‌تست استراتژی', Icons.replay, () => Navigator.push(context, MaterialPageRoute(builder: (_) => const BacktestScreen()))),
      const SizedBox(height: 8),
      _buildButton('⚙️ تنظیمات', Icons.settings, () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SettingsScreen()))),
    ]);
  }

  Widget _buildButton(String text, IconData icon, VoidCallback onTap) {
    return SizedBox(width: double.infinity, height: 50, child: ElevatedButton.icon(onPressed: onTap, icon: Icon(icon, size: 20), label: Text(text, style: const TextStyle(fontSize: 14))));
  }
}
