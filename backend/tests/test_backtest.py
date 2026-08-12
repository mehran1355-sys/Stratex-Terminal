"""
تست‌های سیستم بک‌تست
"""

import unittest
from datetime import datetime, timedelta
from backtest.backtest_engine import (
    BacktestEngine, BacktestConfig, BacktestMode,
    BacktestTrade, BacktestResult,
)
from strategy_engine import Candle


class TestBacktestEngine(unittest.TestCase):
    def setUp(self):
        self.sample_candles = []
        base_price = 1.1000
        base_time = datetime(2023, 1, 1)
        for i in range(100):
            change = (i % 10 - 5) * 0.0010
            o, c = base_price, base_price + change
            h, l = max(o, c) + 0.0020, min(o, c) - 0.0020
            self.sample_candles.append(Candle(open=o, high=h, low=l, close=c, volume=1000, time=base_time + timedelta(days=i)))
            base_price = c
        self.config = BacktestConfig(symbol="EURUSD", timeframe="daily", monitor_timeframe="4h", start_date=datetime(2023, 1, 1), end_date=datetime(2023, 4, 10), initial_balance=10000, total_volume=0.10)

    def test_engine_initialization(self):
        engine = BacktestEngine(self.config)
        self.assertEqual(engine.current_balance, 10000)

    def test_run_with_data(self):
        engine = BacktestEngine(self.config)
        result = engine.run(self.sample_candles[:30], self.sample_candles[:60])
        self.assertIsInstance(result, BacktestResult)

    def test_trade_opening(self):
        engine = BacktestEngine(self.config)
        candle = Candle(open=1.1000, high=1.1050, low=1.0990, close=1.1040, time=datetime(2023, 1, 15))
        signal_data = {'signal': type('Signal', (), {'sl': 1.0950, 'tp1': 1.1100, 'tp2': 1.1150})(), 'direction': 'صعودی'}
        trade = engine._open_trade(signal_data, candle)
        self.assertIsNotNone(trade)
        self.assertEqual(trade.direction, "BUY")

    def test_trade_closing_tp(self):
        engine = BacktestEngine(self.config)
        trade = BacktestTrade(trade_id=1, symbol="EURUSD", direction="BUY", entry_time=datetime(2023, 1, 1), entry_price=1.1000, volume=0.10, stop_loss=1.0950, take_profit_1=1.1100, take_profit_2=1.1150)
        engine.open_positions[1] = trade
        candle = Candle(open=1.1100, high=1.1160, low=1.1090, close=1.1140, time=datetime(2023, 1, 15))
        engine._manage_open_positions(candle)
        self.assertNotIn(1, engine.open_positions)


if __name__ == "__main__":
    unittest.main()
