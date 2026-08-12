"""
انتخاب بازار و سبک معاملاتی
Market & Trading Style Selector
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class MarketType(Enum):
    FOREX = "فارکس"
    STOCKS = "سهام"
    CRYPTO = "ارزهای_دیجیتال"
    IRAN_STOCKS = "بورس_ایران"


class TradingStyle(Enum):
    LONG_TERM = "بلند_مدت"
    MID_TERM = "میان_مدت"
    SCALP = "اسکلپ"
    TICK_TRADE = "تیک_تاکی"


@dataclass
class StrategyInfo:
    strategy_id: str
    name: str
    description: str
    market_type: MarketType
    trading_style: TradingStyle
    timeframes: List[str]
    is_implemented: bool = False
    version: str = "0.0.0"


class StrategyRegistry:
    STRATEGIES = {
        "supply_demand_forex_mid": StrategyInfo("supply_demand_forex_mid", "عرضه و تقاضا - فارکس میان‌مدت", "استراتژی مهران صبابه", MarketType.FOREX, TradingStyle.MID_TERM, ["daily", "weekly", "monthly"], True, "2.0.0"),
        "supply_demand_forex_long": StrategyInfo("supply_demand_forex_long", "عرضه و تقاضا - فارکس بلندمدت", "آینده", MarketType.FOREX, TradingStyle.LONG_TERM, ["monthly"], False),
        "supply_demand_forex_scalp": StrategyInfo("supply_demand_forex_scalp", "عرضه و تقاضا - فارکس اسکلپ", "آینده", MarketType.FOREX, TradingStyle.SCALP, ["15m", "5m"], False),
        "supply_demand_crypto_mid": StrategyInfo("supply_demand_crypto_mid", "عرضه و تقاضا - کریپتو", "آینده", MarketType.CRYPTO, TradingStyle.MID_TERM, ["daily", "4h"], False),
        "supply_demand_stocks_mid": StrategyInfo("supply_demand_stocks_mid", "عرضه و تقاضا - سهام", "آینده", MarketType.STOCKS, TradingStyle.MID_TERM, ["daily", "weekly"], False),
        "supply_demand_iran_stocks": StrategyInfo("supply_demand_iran_stocks", "عرضه و تقاضا - بورس ایران", "آینده", MarketType.IRAN_STOCKS, TradingStyle.MID_TERM, ["daily"], False),
    }

    @classmethod
    def get_implemented(cls) -> List[StrategyInfo]:
        return [s for s in cls.STRATEGIES.values() if s.is_implemented]

    @classmethod
    def get_strategy(cls, sid: str) -> Optional[StrategyInfo]:
        return cls.STRATEGIES.get(sid)

    @classmethod
    def is_market_supported(cls, market: MarketType) -> bool:
        return any(s.market_type == market and s.is_implemented for s in cls.STRATEGIES.values())

    @classmethod
    def is_style_supported(cls, style: TradingStyle) -> bool:
        return any(s.trading_style == style and s.is_implemented for s in cls.STRATEGIES.values())


@dataclass
class UserPreferences:
    user_id: str
    active_markets: Set[MarketType] = field(default_factory=lambda: {MarketType.FOREX})
    active_style: TradingStyle = TradingStyle.MID_TERM
    active_strategy_id: str = "supply_demand_forex_mid"
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MarketSelector:
    def __init__(self):
        self.user_preferences: Dict[str, UserPreferences] = {}

    def set_market(self, user_id: str, market_type: MarketType) -> Dict:
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)
        prefs = self.user_preferences[user_id]
        if not StrategyRegistry.is_market_supported(market_type):
            return {"success": False, "message": f"بازار {market_type.value} فعلاً پشتیبانی نمی‌شود"}
        prefs.active_markets = {market_type}
        prefs.updated_at = datetime.now().isoformat()
        strategy = StrategyRegistry.get_strategy("supply_demand_forex_mid")
        return {"success": True, "message": f"بازار {market_type.value} انتخاب شد", "strategy": {"id": strategy.strategy_id, "name": strategy.name}}

    def set_trading_style(self, user_id: str, style: TradingStyle) -> Dict:
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = UserPreferences(user_id=user_id)
        prefs = self.user_preferences[user_id]
        if not StrategyRegistry.is_style_supported(style):
            return {"success": False, "message": f"سبک {style.value} فعلاً پشتیبانی نمی‌شود"}
        prefs.active_style = style
        prefs.updated_at = datetime.now().isoformat()
        return {"success": True, "message": f"سبک {style.value} انتخاب شد"}

    def get_current_active_strategy(self, user_id: str) -> Optional[StrategyInfo]:
        if user_id not in self.user_preferences:
            return StrategyRegistry.get_strategy("supply_demand_forex_mid")
        return StrategyRegistry.get_strategy(self.user_preferences[user_id].active_strategy_id)

    def get_supported_markets(self) -> List[Dict]:
        return [{"market": m.value, "is_supported": StrategyRegistry.is_market_supported(m)} for m in MarketType]

    def get_supported_styles(self) -> List[Dict]:
        return [{"style": s.value, "is_supported": StrategyRegistry.is_style_supported(s)} for s in TradingStyle]

    def get_available_markets_display(self) -> str:
        lines = ["📊 وضعیت بازارها:", "=" * 40]
        for m in MarketType:
            supported = StrategyRegistry.is_market_supported(m)
            lines.append(f"{'✅' if supported else '⏳'} {m.value}")
        return "\n".join(lines)
