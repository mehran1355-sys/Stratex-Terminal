import 'package:flutter/material.dart';

class LotInputWidget extends StatelessWidget {
  final double value;
  final double min;
  final double max;
  final double step;
  final ValueChanged<double> onChanged;

  const LotInputWidget({
    super.key,
    required this.value,
    required this.min,
    required this.max,
    required this.step,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('حداقل: ${min.toStringAsFixed(2)}', style: TextStyle(fontSize: 10, color: Colors.grey[600])),
            Text('حداکثر: ${max.toStringAsFixed(1)}', style: TextStyle(fontSize: 10, color: Colors.grey[600])),
          ],
        ),
        Slider(
          value: value.clamp(min, max),
          min: min,
          max: max,
          divisions: ((max - min) / step).round().clamp(1, 1000),
          activeColor: AppTheme.accentColor,
          inactiveColor: Colors.grey[800],
          onChanged: onChanged,
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _buildAdjustButton(Icons.remove, () {
              final newValue = (value - step).clamp(min, max);
              onChanged(double.parse(newValue.toStringAsFixed(2)));
            }),
            const SizedBox(width: 16),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
              decoration: BoxDecoration(
                color: AppTheme.primaryColor.withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.accentColor.withOpacity(0.5)),
              ),
              child: Text(
                value.toStringAsFixed(2),
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.accentColor),
              ),
            ),
            const SizedBox(width: 16),
            _buildAdjustButton(Icons.add, () {
              final newValue = (value + step).clamp(min, max);
              onChanged(double.parse(newValue.toStringAsFixed(2)));
            }),
          ],
        ),
      ],
    );
  }

  Widget _buildAdjustButton(IconData icon, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: AppTheme.surfaceColor,
          shape: BoxShape.circle,
          border: Border.all(color: Colors.white24),
        ),
        child: Icon(icon, color: Colors.white, size: 20),
      ),
    );
  }
}
