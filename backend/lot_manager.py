"""
مدیریت لات بر اساس نوع دارایی
Lot Manager Module
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AssetType(Enum):
    FOREX_PAIRS = "جفت_ارزها"
    COMMODITIES = "کالاها"
    INDICES = "شاخص_ها"
    STOCKS = "سهام"
    CRYPTO = "ارزهای_دیجیتال"


@dataclass
class LotConfig:
    asset_type: AssetType
    default_lot: float
    min_lot: float
    max_lot: float
    lot_step: float
    risk_per_lot: float


DEFAULT_LOT_SETTINGS = {
    AssetType.FOREX_PAIRS: LotConfig(AssetType.FOREX_PAIRS, 0.10, 0.01, 50.0, 0.01, 10.0),
    AssetType.COMMODITIES: LotConfig(AssetType.COMMODITIES, 0.05, 0.01, 20.0, 0.01, 100.0),
    AssetType.INDICES: LotConfig(AssetType.INDICES, 1.0, 0.10, 100.0, 0.10, 50.0),
    AssetType.STOCKS: LotConfig(AssetType.STOCKS, 10.0, 1.0, 10000.0, 1.0, 0.0),
    AssetType.CRYPTO: LotConfig(AssetType.CRYPTO, 0.10, 0.01, 10.0, 0.01, 50.0),
}


class SymbolClassifier:
    SYMBOL_MAPPING = {
        "EURUSD": AssetType.FOREX_PAIRS, "GBPUSD": AssetType.FOREX_PAIRS, "USDJPY": AssetType.FOREX_PAIRS,
        "AUDUSD": AssetType.FOREX_PAIRS, "USDCAD": AssetType.FOREX_PAIRS, "NZDUSD": AssetType.FOREX_PAIRS,
        "EURGBP": AssetType.FOREX_PAIRS, "EURJPY": AssetType.FOREX_PAIRS, "GBPJPY": AssetType.FOREX_PAIRS,
        "XAUUSD": AssetType.COMMODITIES, "XAGUSD": AssetType.COMMODITIES, "GOLD": AssetType.COMMODITIES,
        "US30": AssetType.INDICES, "NAS100": AssetType.INDICES, "SPX500": AssetType.INDICES,
        "BTCUSD": AssetType.CRYPTO, "ETHUSD": AssetType.CRYPTO,
    }

    @classmethod
    def classify(cls, symbol: str) -> AssetType:
        upper = symbol.upper().strip()
        if upper in cls.SYMBOL_MAPPING:
            return cls.SYMBOL_MAPPING[upper]
        if upper.startswith("XAU") or upper.startswith("XAG"):
            return AssetType.COMMODITIES
        if any(x in upper for x in ["US30", "NAS", "SPX", "GER", "UK", "JPN", "AUS"]):
            return AssetType.INDICES
        if upper.startswith(("BTC", "ETH", "XRP", "LTC", "BCH", "ADA")):
            return AssetType.CRYPTO
        if len(upper) == 6 and upper[3:] in ["USD", "JPY", "CHF", "CAD", "AUD", "NZD", "GBP"]:
            return AssetType.FOREX_PAIRS
        return AssetType.FOREX_PAIRS


class LotManager:
    def __init__(self):
        self.user_lot_settings: Dict[AssetType, LotConfig] = {}
        self._load_defaults()

    def _load_defaults(self):
        self.user_lot_settings = DEFAULT_LOT_SETTINGS.copy()

    def set_lot_for_asset_type(self, asset_type: AssetType, default_lot: float) -> LotConfig:
        config = LotConfig(asset_type, default_lot, default_lot * 0.1, default_lot * 100, 0.01 if default_lot < 1 else 0.10, DEFAULT_LOT_SETTINGS[asset_type].risk_per_lot)
        self.user_lot_settings[asset_type] = config
        return config

    def set_lot_for_forex(self, lot: float): return self.set_lot_for_asset_type(AssetType.FOREX_PAIRS, lot)
    def set_lot_for_commodities(self, lot: float): return self.set_lot_for_asset_type(AssetType.COMMODITIES, lot)
    def set_lot_for_indices(self, lot: float): return self.set_lot_for_asset_type(AssetType.INDICES, lot)
    def set_lot_for_crypto(self, lot: float): return self.set_lot_for_asset_type(AssetType.CRYPTO, lot)

    def get_lot_for_symbol(self, symbol: str) -> float:
        asset_type = SymbolClassifier.classify(symbol)
        config = self.user_lot_settings.get(asset_type)
        return config.default_lot if config else 0.10

    def get_lot_config_for_symbol(self, symbol: str) -> LotConfig:
        asset_type = SymbolClassifier.classify(symbol)
        return self.user_lot_settings.get(asset_type, DEFAULT_LOT_SETTINGS[AssetType.FOREX_PAIRS])

    def get_all_lot_settings(self) -> Dict:
        return {at.value: {"default_lot": c.default_lot, "min_lot": c.min_lot, "max_lot": c.max_lot} for at, c in self.user_lot_settings.items()}

    def calculate_lot_by_risk(self, symbol: str, balance: float, risk_pct: float, sl_pips: float) -> float:
        config = self.get_lot_config_for_symbol(symbol)
        risk_amount = balance * (risk_pct / 100)
        pip_value = config.risk_per_lot / config.lot_step
        if pip_value == 0 or sl_pips == 0:
            return config.default_lot
        lot = risk_amount / (sl_pips * pip_value)
        lot = max(config.min_lot, min(lot, config.max_lot))
        return round(lot / config.lot_step) * config.lot_step

    def validate_lot(self, symbol: str, lot: float) -> tuple:
        config = self.get_lot_config_for_symbol(symbol)
        if lot < config.min_lot:
            return False, f"لات {lot} کمتر از حداقل {config.min_lot}"
        if lot > config.max_lot:
            return False, f"لات {lot} بیشتر از حداکثر {config.max_lot}"
        return True, "✅ معتبر"
