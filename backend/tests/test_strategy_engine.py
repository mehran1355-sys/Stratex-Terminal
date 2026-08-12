"""
تست‌های موتور استراتژی
"""

import unittest
from datetime import datetime
from strategy_engine import (
    Candle, CandleSize, CandleDirection,
    CandleSizeCalculator, ShadowAnalyzer,
    OrangeLineDrawer, OrangeLines,
    MarketMonitor, BreakType,
)


class TestCandle(unittest.TestCase):
    def test_bullish_candle(self):
        candle = Candle(open=1.1000, high=1.1100, low=1.0950, close=1.1080)
        self.assertEqual(candle.direction, CandleDirection.BULLISH)
        self.assertAlmostEqual(candle.body_size, 0.0080)

    def test_bearish_candle(self):
        candle = Candle(open=1.1000, high=1.1050, low=1.0900, close=1.0920)
        self.assertEqual(candle.direction, CandleDirection.BEARISH)
        self.assertAlmostEqual(candle.body_size, 0.0080)

    def test_shadows(self):
        candle = Candle(open=1.1000, high=1.1150, low=1.0900, close=1.1100)
        self.assertAlmostEqual(candle.upper_shadow, 0.0050)
        self.assertAlmostEqual(candle.lower_shadow, 0.0100)


class TestCandleSizeCalculator(unittest.TestCase):
    def setUp(self):
        self.candles = [Candle(open=1.1000, high=1.1050, low=1.0950, close=1.1040) for _ in range(30)]

    def test_calculate_daily(self):
        size, ratio = CandleSizeCalculator.calculate(self.candles, "daily")
        self.assertIsInstance(size, CandleSize)


class TestShadowAnalyzer(unittest.TestCase):
    def test_long_shadow(self):
        candle = Candle(open=1.1000, high=1.1200, low=1.0990, close=1.1010)
        is_long = ShadowAnalyzer.is_long_shadow(candle, CandleSize.VERY_LONG, "daily", "upper")
        self.assertTrue(is_long)


class TestOrangeLineDrawer(unittest.TestCase):
    def test_bullish_very_long(self):
        candle = Candle(open=1.1000, high=1.1200, low=1.0950, close=1.1180)
        orange = OrangeLineDrawer.draw(candle, CandleSize.VERY_LONG, "daily")
        self.assertIsInstance(orange, OrangeLines)
        self.assertGreater(orange.upper, orange.lower)


class TestMarketMonitor(unittest.TestCase):
    def test_initial_break(self):
        orange = OrangeLines(upper=1.1100, lower=1.0900)
        candles = [Candle(open=1.1050, high=1.1120, low=1.1040, close=1.1080)]
        result = MarketMonitor.evaluate(candles, orange)
        self.assertEqual(result["break_type"], BreakType.INITIAL)

    def test_complete_break(self):
        orange = OrangeLines(upper=1.1100, lower=1.0900)
        candles = [
            Candle(open=1.1050, high=1.1120, low=1.1040, close=1.1120),
            Candle(open=1.1120, high=1.1150, low=1.1100, close=1.1140),
        ]
        result = MarketMonitor.evaluate(candles, orange)
        self.assertEqual(result["break_type"], BreakType.COMPLETE)


if __name__ == "__main__":
    unittest.main()
