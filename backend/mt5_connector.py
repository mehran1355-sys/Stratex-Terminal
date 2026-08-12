"""
اتصال به MetaTrader 5
MT5 Connector Module
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    logger.warning("MetaTrader5 not installed - running in simulation mode")

from strategy_engine import Candle


class MT5Connector:
    TF_MAPPING = {
        "monthly": mt5.TIMEFRAME_MN1 if MT5_AVAILABLE else None,
        "weekly": mt5.TIMEFRAME_W1 if MT5_AVAILABLE else None,
        "daily": mt5.TIMEFRAME_D1 if MT5_AVAILABLE else None,
        "12h": mt5.TIMEFRAME_H12 if MT5_AVAILABLE else None,
        "8h": mt5.TIMEFRAME_H8 if MT5_AVAILABLE else None,
        "6h": mt5.TIMEFRAME_H6 if MT5_AVAILABLE else None,
        "4h": mt5.TIMEFRAME_H4 if MT5_AVAILABLE else None,
        "2h": mt5.TIMEFRAME_H2 if MT5_AVAILABLE else None,
        "1h": mt5.TIMEFRAME_H1 if MT5_AVAILABLE else None,
        "30m": mt5.TIMEFRAME_M30 if MT5_AVAILABLE else None,
        "15m": mt5.TIMEFRAME_M15 if MT5_AVAILABLE else None,
        "10m": mt5.TIMEFRAME_M10 if MT5_AVAILABLE else None,
        "5m": mt5.TIMEFRAME_M5 if MT5_AVAILABLE else None,
        "3m": mt5.TIMEFRAME_M3 if MT5_AVAILABLE else None,
        "2m": mt5.TIMEFRAME_M2 if MT5_AVAILABLE else None,
        "1m": mt5.TIMEFRAME_M1 if MT5_AVAILABLE else None,
    }

    def __init__(self):
        self.connected = False
        self._initialize()

    def _initialize(self):
        if not MT5_AVAILABLE:
            logger.info("MT5 not available - simulation mode")
            return
        try:
            if not mt5.initialize():
                raise ConnectionError(f"MT5 init failed: {mt5.last_error()}")
            self.connected = True
            logger.info("✅ Connected to MT5")
        except Exception as e:
            logger.error(f"MT5 connection error: {e}")
            self.connected = False

    def get_candles(self, symbol: str, timeframe: str, count: int = 100) -> List[Candle]:
        if not self.connected:
            return self._generate_sample_candles(count)
        mt5_tf = self.TF_MAPPING.get(timeframe)
        if not mt5_tf:
            return []
        try:
            rates = mt5.copy_rates_from_pos(symbol, mt5_tf, 0, count)
            if rates is None or len(rates) == 0:
                return []
            candles = []
            for r in rates:
                dt = datetime.fromtimestamp(r["time"])
                candles.append(Candle(open=r["open"], high=r["high"], low=r["low"], close=r["close"], volume=r["tick_volume"], time=dt, symbol=symbol, timeframe=timeframe))
            return candles
        except Exception as e:
            logger.error(f"Error getting candles: {e}")
            return []

    def get_multi_timeframe_data(self, symbol: str, timeframes: List[str]) -> Dict[str, List[Candle]]:
        result = {}
        for tf in timeframes:
            candles = self.get_candles(symbol, tf, 200)
            if candles:
                result[tf] = candles
        return result

    def get_account_info(self) -> Dict:
        if not self.connected:
            return {"balance": 10000, "equity": 10000, "margin": 0, "currency": "USD"}
        info = mt5.account_info()
        return {"balance": info.balance, "equity": info.equity, "margin": info.margin, "currency": info.currency} if info else {}

    def send_order(self, symbol: str, order_type: str, volume: float, price: float, sl: float, tp: float, comment: str = "SD_Bot") -> Optional[int]:
        if not self.connected:
            logger.info(f"[SIM] {order_type} {symbol} @ {price}")
            return None
        action = mt5.ORDER_TYPE_BUY_LIMIT if order_type == "BUY_LIMIT" else mt5.ORDER_TYPE_SELL_LIMIT
        request = {"action": mt5.TRADE_ACTION_PENDING, "symbol": symbol, "volume": float(volume), "type": action, "price": price, "sl": sl, "tp": tp, "deviation": 10, "magic": 123456, "comment": comment, "type_time": mt5.ORDER_TIME_GTC, "type_filling": mt5.ORDER_FILLING_IOC}
        result = mt5.order_send(request)
        return result.order if result.retcode == mt5.TRADE_RETCODE_DONE else None

    def close_position(self, ticket: int) -> bool:
        if not self.connected:
            return True
        position = mt5.positions_get(ticket=ticket)
        if not position:
            return False
        pos = position[0]
        tick = mt5.symbol_info_tick(pos.symbol)
        type_dict = {mt5.ORDER_TYPE_BUY: mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL: mt5.ORDER_TYPE_BUY}
        price = tick.bid if pos.type == mt5.ORDER_TYPE_BUY else tick.ask
        request = {"action": mt5.TRADE_ACTION_DEAL, "position": pos.ticket, "symbol": pos.symbol, "volume": pos.volume, "type": type_dict[pos.type], "price": price, "deviation": 10, "magic": 123456, "comment": "Close"}
        result = mt5.order_send(request)
        return result.retcode == mt5.TRADE_RETCODE_DONE

    def _generate_sample_candles(self, count: int) -> List[Candle]:
        candles = []
        base = 1.1000
        for i in range(count):
            change = (i % 10 - 5) * 0.0010
            o, c = base, base + change
            h, l = max(o, c) + 0.0020, min(o, c) - 0.0020
            candles.append(Candle(open=o, high=h, low=l, close=c, volume=1000, time=datetime.now() - __import__('datetime').timedelta(days=count-i)))
            base = c
        return candles
