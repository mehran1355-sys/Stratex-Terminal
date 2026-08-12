import 'package:flutter/material.dart';
import '../services/api_service.dart';

class StyleSelectorWidget extends StatefulWidget {
  const StyleSelectorWidget({super.key});
  @override
  State<StyleSelectorWidget> createState() => _StyleSelectorWidgetState();
}

class _StyleSelectorWidgetState extends State<StyleSelectorWidget> {
  String _selected = 'mid_term';

  @override
  Widget build(BuildContext context) {
    final styles = {"long_term": ["📅", "بلندمدت", false], "mid_term": ["📊", "میان‌مدت", true], "scalp": ["⚡", "اسکلپ", false], "tick_trade": ["🎯", "تیک‌تاکی", false]};
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('سبک معاملاتی', style: TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          ...styles.entries.map((e) {
            final isSel = _selected == e.key;
            final avail = e.value[2] as bool;
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: InkWell(
                onTap: avail ? () async { await ApiService().selectStyle('default', e.key); setState(() => _selected = e.key); } : null,
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(color: isSel ? AppTheme.primaryColor.withOpacity(0.3) : AppTheme.surfaceColor, borderRadius: BorderRadius.circular(8), border: Border.all(color: isSel ? AppTheme.accentColor : Colors.white12)),
                  child: Row(children: [
                    Text(e.value[0] as String, style: const TextStyle(fontSize: 24)),
                    const SizedBox(width: 12),
                    Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(e.value[1] as String, style: TextStyle(fontWeight: isSel ? FontWeight.bold : FontWeight.normal)), if (!avail) const Text('به زودی', style: TextStyle(fontSize: 10, color: Colors.orange))])),
                    if (isSel) const Icon(Icons.check_circle, color: AppTheme.successColor, size: 20),
                  ]),
                ),
              ),
            );
          }),
        ]),
      ),
    );
  }
}
