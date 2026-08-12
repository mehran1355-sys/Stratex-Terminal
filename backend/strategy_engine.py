"""
استراتژی روانشناسی عرضه و تقاضا
Supply & Demand Psychology Strategy - Core Engine
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Enums
# ============================================================

class CandleSize(Enum):
    VERY_LONG = "خیلی_بلند"
    LONG = "بلند"
    SHORT = "کوتاه"
    VERY_SHORT = "خیلی_کوتاه"


class CandleDirection(Enum):
    BULLISH = "صعودی"
    BEARISH = "نزولی"


class BreakType(Enum):
    NONE = "هیچ"
    INITIAL = "شکست_اولیه"
    COMPLETE = "شکست_تکمیلی"


class TradeStatus(Enum):
    PENDING = "در_انتظار"
    ACTIVE = "فعال"
    TP1_HIT = "حد_سود_اول"
    TP2_HIT = "حد_سود_دوم"
    SL_HIT = "حد_ضرر"
    CANCELLED = "ابطال_شده"
    EXPIRED = "منقضی_شده"


# ============================================================
# Data Classes
# ============================================================

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    time: Optional[datetime] = None
    symbol: str = ""
    timeframe: str = ""

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def direction(self) -> CandleDirection:
        return CandleDirection.BULLISH if self.close >= self.open else CandleDirection.BEARISH

    @property
    def upper_shadow(self) -> float:
        return (self.high - self.close) if self.direction == CandleDirection.BULLISH else (self.high - self.open)

    @property
    def lower_shadow(self) -> float:
        return (self.open - self.low) if self.direction == CandleDirection.BULLISH else (self.close - self.low)

    @property
    def is_doji(self) -> bool:
        return self.body_size <= (self.high - self.low) * 0.1


@dataclass
class OrangeLines:
    upper: float
    lower: float

    @property
    def height(self) -> float:
        return abs(self.upper - self.lower)


@dataclass
class TradingZones:
    near_zone: Tuple[float, float]
    middle_zone: Tuple[float, float]
    far_zone: Tuple[float, float]
    pattern_direction: str


@dataclass
class PurpleLine:
    price: float
    is_above: bool
    timeframe: str
    is_fallback: bool = False


@dataclass
class TradeSignal:
    symbol: str
    timeframe: str
    pattern_direction: str
    break_type: BreakType
    zones: TradingZones
    orange_lines: OrangeLines
    purple_upper: PurpleLine
    purple_lower: PurpleLine
    entry_plan: Dict[str, List[Dict]] = field(default_factory=dict)
    tp1: float = 0.0
    tp2: float = 0.0
    sl: float = 0.0
    total_volume: float = 0.01
    created_at: datetime = field(default_factory=datetime.now)
    status: TradeStatus = TradeStatus.PENDING
    tp1_already_hit: bool = False
    cancellation_reason: str = ""


# ============================================================
# Candle Size Calculator
# ============================================================

class CandleSizeCalculator:
    LOOKBACK_PERIODS = {"monthly": 12, "weekly": 24, "daily": 30}

    @classmethod
    def calculate(cls, candles: List[Candle], timeframe: str) -> Tuple[CandleSize, float]:
        n = cls.LOOKBACK_PERIODS.get(timeframe, 30)
        recent = candles[-n:] if len(candles) >= n else candles
        if len(recent) < 2:
            return CandleSize.SHORT, 0.0
        analysis_candle = recent[-1]
        bodies = [c.body_size for c in recent]
        sorted_bodies = sorted(bodies, reverse=True)
        top_two_avg = (sorted_bodies[0] + sorted_bodies[1]) / 2.0
        if top_two_avg == 0:
            return CandleSize.VERY_SHORT, 0.0
        ratio = analysis_candle.body_size / top_two_avg
        if ratio >= 0.6:
            return CandleSize.VERY_LONG, ratio
        elif 0.4 <= ratio < 0.6:
            return CandleSize.LONG, ratio
        elif 0.1 <= ratio < 0.4:
            return CandleSize.SHORT, ratio
        else:
            return CandleSize.VERY_SHORT, ratio


# ============================================================
# Shadow Analyzer
# ============================================================

class ShadowAnalyzer:
    @staticmethod
    def is_long_shadow(candle: Candle, candle_size: CandleSize, timeframe: str, shadow_type: str) -> bool:
        body = candle.body_size
        if body == 0:
            return True
        shadow = candle.upper_shadow if shadow_type == "upper" else candle.lower_shadow
        if timeframe in ["monthly", "weekly"]:
            if candle_size in [CandleSize.VERY_LONG, CandleSize.LONG]:
                return shadow >= body
            else:
                return shadow >= (2.0 * body)
        else:
            if candle_size in [CandleSize.VERY_LONG, CandleSize.LONG]:
                return shadow >= (1.5 * body)
            else:
                return shadow >= (2.5 * body)


# ============================================================
# Orange Line Drawer
# ============================================================

class OrangeLineDrawer:
    @staticmethod
    def draw(candle: Candle, candle_size: CandleSize, timeframe: str) -> OrangeLines:
        body = candle.body_size
        upper_long = ShadowAnalyzer.is_long_shadow(candle, candle_size, timeframe, "upper")
        lower_long = ShadowAnalyzer.is_long_shadow(candle, candle_size, timeframe, "lower")

        if candle.direction == CandleDirection.BULLISH:
            if candle_size == CandleSize.VERY_LONG:
                line1 = candle.close - (0.25 * body)
            elif candle_size == CandleSize.LONG:
                line1 = candle.open + (0.50 * body)
            else:
                line1 = (candle.low + 0.5 * candle.lower_shadow) if lower_long else candle.low

            if candle_size in [CandleSize.VERY_LONG, CandleSize.LONG]:
                line2 = (candle.close + 0.5 * candle.upper_shadow) if upper_long else candle.high
            else:
                line2 = (candle.high - 0.5 * candle.upper_shadow) if upper_long else candle.high
        else:
            if candle_size == CandleSize.VERY_LONG:
                line1 = candle.close + (0.25 * body)
            elif candle_size == CandleSize.LONG:
                line1 = candle.open - (0.50 * body)
            else:
                line1 = (candle.high - 0.5 * candle.upper_shadow) if upper_long else candle.high

            if candle_size in [CandleSize.VERY_LONG, CandleSize.LONG]:
                line2 = (candle.close - 0.5 * candle.lower_shadow) if lower_long else candle.low
            else:
                line2 = (candle.low + 0.5 * candle.lower_shadow) if lower_long else candle.low

        return OrangeLines(upper=max(line1, line2), lower=min(line1, line2))


# ============================================================
# Purple Line Calculator
# ============================================================

class PurpleLineCalculator:
    TF_HIERARCHY = {"monthly": ["monthly", "weekly", "daily"], "weekly": ["weekly", "daily", "4h"], "daily": ["daily", "4h", "1h"]}

    @classmethod
    def calculate_purple_lines(cls, multi_tf_data: Dict[str, List[Candle]], base_tf: str, orange: OrangeLines) -> Dict[str, PurpleLine]:
        upper = cls._find_purple(multi_tf_data, base_tf, orange, True)
        lower = cls._find_purple(multi_tf_data, base_tf, orange, False)
        return {"upper": upper, "lower": lower}

    @classmethod
    def _find_purple(cls, multi_tf_data: Dict[str, List[Candle]], base_tf: str, orange: OrangeLines, is_above: bool) -> PurpleLine:
        tf_sequence = cls.TF_HIERARCHY.get(base_tf, [base_tf])
        zone_h = orange.height
        ref_price = orange.upper if is_above else orange.lower

        for current_tf in tf_sequence[:3]:
            candles = multi_tf_data.get(current_tf, [])
            if not candles:
                continue
            candidates = []
            for i in range(len(candles) - 2, -1, -1):
                if len(candidates) >= 5:
                    break
                c = candles[i]
                next_c = candles[i + 1] if i + 1 < len(candles) else None
                if not next_c:
                    continue
                exited = (c.high > orange.upper and c.open < orange.upper) if is_above else (c.low < orange.lower and c.open > orange.lower)
                if exited and cls._check_reversal(c, next_c, orange, is_above):
                    candidates.append(c.high if is_above else c.low)

            valid = [p for p in candidates if 0.20 * zone_h <= abs(p - ref_price) <= 2.0 * zone_h]
            if valid:
                closest = min(valid, key=lambda p: abs(p - ref_price))
                return PurpleLine(price=closest, is_above=is_above, timeframe=current_tf)

        fallback = (orange.upper + 0.25 * zone_h) if is_above else (orange.lower - 0.25 * zone_h)
        return PurpleLine(price=fallback, is_above=is_above, timeframe=f"{base_tf}_fallback", is_fallback=True)

    @staticmethod
    def _check_reversal(candle: Candle, next_candle: Candle, orange: OrangeLines, is_above: bool) -> bool:
        body = candle.body_size
        if body == 0:
            return False
        if orange.lower <= candle.close <= orange.upper and orange.lower <= candle.open <= orange.upper:
            return True
        if is_above and candle.upper_shadow >= body * 2:
            return True
        if not is_above and candle.lower_shadow >= body * 2:
            return True
        if is_above and candle.close > orange.upper and next_candle.close < next_candle.open:
            if (candle.close - next_candle.close) >= 0.5 * body:
                return True
        if not is_above and candle.close < orange.lower and next_candle.close > next_candle.open:
            if (next_candle.close - candle.close) >= 0.5 * body:
                return True
        if is_above and (candle.close - next_candle.low) >= 0.5 * body:
            return True
        if not is_above and (next_candle.high - candle.close) >= 0.5 * body:
            return True
        return False


# ============================================================
# Market Monitor
# ============================================================

class MarketMonitor:
    @staticmethod
    def get_monitoring_timeframe(analysis_tf: str) -> str:
        mapping = {"monthly": "daily", "weekly": "4h", "daily": "1h"}
        return mapping.get(analysis_tf, "1h")

    @classmethod
    def evaluate(cls, monitor_candles: List[Candle], orange: OrangeLines) -> Dict:
        first_touched = None
        outside_closes = 0
        for c in monitor_candles:
            if first_touched is None:
                if c.high >= orange.upper:
                    first_touched = "upper"
                elif c.low <= orange.lower:
                    first_touched = "lower"
            if c.close > orange.upper or c.close < orange.lower:
                outside_closes += 1

        break_type = BreakType.COMPLETE if outside_closes >= 2 else (BreakType.INITIAL if first_touched else BreakType.NONE)
        step = orange.height / 3.0
        div1, div2 = orange.lower + step, orange.lower + 2.0 * step

        if first_touched == "upper":
            zones = TradingZones(near_zone=(div2, orange.upper), middle_zone=(div1, div2), far_zone=(orange.lower, div1), pattern_direction="صعودی")
        else:
            zones = TradingZones(near_zone=(orange.lower, div1), middle_zone=(div1, div2), far_zone=(div2, orange.upper), pattern_direction="نزولی")

        return {"first_touched": first_touched, "break_type": break_type, "pattern_direction": zones.pattern_direction, "zones": zones}


# ============================================================
# Entry Plan Builder
# ============================================================

class EntryPlanBuilder:
    @staticmethod
    def build(zones: TradingZones, break_type: BreakType, pattern_direction: str, total_volume: float, split_count: int = 2) -> Dict[str, List[Dict]]:
        entry_plan = {}
        if break_type == BreakType.INITIAL:
            entry_plan["middle"] = []
            entry_plan["far"] = EntryPlanBuilder._split_zone(zones.far_zone, total_volume, split_count, pattern_direction)
        elif break_type == BreakType.COMPLETE:
            half = total_volume / 2.0
            entry_plan["middle"] = EntryPlanBuilder._split_zone(zones.middle_zone, half, split_count, pattern_direction)
            entry_plan["far"] = EntryPlanBuilder._split_zone(zones.far_zone, half, split_count, pattern_direction)
        return entry_plan

    @staticmethod
    def _split_zone(zone: Tuple[float, float], total_volume: float, split_count: int, pattern_direction: str) -> List[Dict]:
        zone_low, zone_high = zone
        zone_range = zone_high - zone_low
        entries = []
        ratios = [0.30, 0.30, 0.40] if split_count == 3 else ([0.50, 0.50] if split_count == 2 else [1.0])
        positions = [0.16, 0.50, 0.84] if split_count == 3 else ([0.33, 0.66] if split_count == 2 else [0.50])
        for i, ratio in enumerate(ratios):
            price = zone_high - (zone_range * positions[i]) if pattern_direction == "صعودی" else zone_low + (zone_range * positions[i])
            entries.append({"price": round(price, 5), "volume": round(total_volume * ratio, 4), "percentage": round(ratio * 100, 1), "zone_part": i + 1})
        return entries


# ============================================================
# Trade Validator
# ============================================================

class TradeValidator:
    @staticmethod
    def check_cancellation_rules(signal: TradeSignal, monitor_candles: List[Candle], current_price: float, already_entered: bool = False) -> Tuple[bool, str]:
        if not already_entered:
            for c in monitor_candles:
                if signal.pattern_direction == "صعودی":
                    if c.high >= signal.tp2:
                        return False, f"⛔ ابطال: TP2 قبل از ورود تاچ شده"
                else:
                    if c.low <= signal.tp2:
                        return False, f"⛔ ابطال: TP2 قبل از ورود تاچ شده"
        if signal.tp1_already_hit and not already_entered:
            if signal.pattern_direction == "صعودی" and current_price <= signal.orange_lines.upper:
                return False, "⛔ ابطال: برگشت بعد از TP1"
            if signal.pattern_direction == "نزولی" and current_price >= signal.orange_lines.lower:
                return False, "⛔ ابطال: برگشت بعد از TP1"
        return True, "✅ معتبر"


# ============================================================
# Trade Signal Builder
# ============================================================

class TradeSignalBuilder:
    @staticmethod
    def build(symbol: str, analysis_tf: str, orange: OrangeLines, purple_dict: Dict[str, PurpleLine], monitor_result: Dict, total_volume: float, split_count: int = 2) -> Optional[TradeSignal]:
        break_type = monitor_result["break_type"]
        zones = monitor_result["zones"]
        pattern_dir = monitor_result["pattern_direction"]
        if break_type == BreakType.NONE or pattern_dir == "نامشخص":
            return None
        upper_purple, lower_purple = purple_dict["upper"], purple_dict["lower"]
        tp1 = orange.upper if pattern_dir == "صعودی" else orange.lower
        tp2 = upper_purple.price if pattern_dir == "صعودی" else lower_purple.price
        sl = lower_purple.price if pattern_dir == "صعودی" else upper_purple.price
        entry_plan = EntryPlanBuilder.build(zones, break_type, pattern_dir, total_volume, split_count)
        return TradeSignal(symbol=symbol, timeframe=analysis_tf, pattern_direction=pattern_dir, break_type=break_type, zones=zones, orange_lines=orange, purple_upper=upper_purple, purple_lower=lower_purple, entry_plan=entry_plan, tp1=tp1, tp2=tp2, sl=sl, total_volume=total_volume)


# ============================================================
# Timeframe End Checker
# ============================================================

class TimeframeEndChecker:
    @staticmethod
    def should_close_positions(tf: str, current_time: datetime) -> bool:
        if tf == "monthly":
            next_month = current_time.replace(day=28) + timedelta(days=4)
            return current_time.date() == (next_month - timedelta(days=next_month.day)).date()
        elif tf == "weekly":
            return current_time.weekday() == 4
        elif tf == "daily":
            return current_time.hour == 23 and current_time.minute >= 55
        return False


# ============================================================
# Strategy Engine
# ============================================================

class StrategyEngine:
    def __init__(self):
        self.active_signals: Dict[str, TradeSignal] = {}

    def analyze(self, symbol: str, multi_tf_data: Dict[str, List[Candle]], analysis_tf: str, total_volume: float = 0.01, split_count: int = 2) -> Optional[TradeSignal]:
        analysis_candles = multi_tf_data.get(analysis_tf, [])
        if len(analysis_candles) < 2:
            return None
        analysis_candle = analysis_candles[-1]
        candle_size, _ = CandleSizeCalculator.calculate(analysis_candles, analysis_tf)
        orange = OrangeLineDrawer.draw(analysis_candle, candle_size, analysis_tf)
        purple_dict = PurpleLineCalculator.calculate_purple_lines(multi_tf_data, analysis_tf, orange)
        monitor_tf = MarketMonitor.get_monitoring_timeframe(analysis_tf)
        monitor_candles = multi_tf_data.get(monitor_tf, [])
        if not monitor_candles:
            return None
        monitor_result = MarketMonitor.evaluate(monitor_candles, orange)
        signal = TradeSignalBuilder.build(symbol, analysis_tf, orange, purple_dict, monitor_result, total_volume, split_count)
        if signal:
            is_valid, reason = TradeValidator.check_cancellation_rules(signal, monitor_candles, monitor_candles[-1].close)
            if not is_valid:
                signal.status = TradeStatus.CANCELLED
                signal.cancellation_reason = reason
            self.active_signals[f"{symbol}_{analysis_tf}"] = signal
        return signal
