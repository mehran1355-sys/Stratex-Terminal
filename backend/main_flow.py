"""
ارکستراتور اصلی - چرخه کامل سیستم
Main Flow Orchestrator
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

from strategy_engine import StrategyEngine, TradeStatus, MarketMonitor
from mt5_connector import MT5Connector
from risk_manager import RiskManager
from trade_executor import TradeExecutor
from lot_manager import LotManager
from market_selector import MarketSelector


class TradingSystemOrchestrator:
    def __init__(self, mt5: MT5Connector, strategy: StrategyEngine, executor: TradeExecutor, risk: RiskManager, lot: LotManager, market: MarketSelector, telegram=None):
        self.mt5 = mt5
        self.strategy_engine = strategy
        self.trade_executor = executor
        self.risk_manager = risk
        self.lot_manager = lot
        self.market_selector = market
        self.telegram = telegram

    async def run_full_cycle(self, user_id: str = "default", symbols: List[str] = None, auto_trade: bool = False) -> List[Dict]:
        logger.info(f"Starting full cycle for {user_id}")
        strategy = self.market_selector.get_current_active_strategy(user_id)
        if not symbols:
            symbols = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD"]
        results = []
        for symbol in symbols:
            timeframes = strategy.timeframes if strategy else ["daily"]
            monitor_tf = MarketMonitor.get_monitoring_timeframe(timeframes[0])
            all_tfs = list(set(timeframes + [monitor_tf]))
            multi_tf = self.mt5.get_multi_timeframe_data(symbol, all_tfs)
            if not multi_tf:
                continue
            for tf in timeframes:
                signal = self.strategy_engine.analyze(symbol, multi_tf, tf)
                if signal and signal.status != TradeStatus.CANCELLED:
                    orders = self.trade_executor.place_entry_orders_from_plan(signal, user_confirmed=auto_trade)
                    results.append({"symbol": symbol, "timeframe": tf, "orders": orders})
                    logger.info(f"✅ {symbol} {tf}: {orders.get('total_orders', 0)} orders")
        return results

    async def monitor_active_positions(self):
        while True:
            for ticket, order in self.trade_executor.pending_orders.items():
                pass
            await asyncio.sleep(10)

    async def check_timeframe_end(self):
        from strategy_engine import TimeframeEndChecker
        now = datetime.now()
        for tf in ["monthly", "weekly", "daily"]:
            if TimeframeEndChecker.should_close_positions(tf, now):
                logger.info(f"⏰ Timeframe end: {tf}")
                self.trade_executor.close_positions_at_timeframe_end(tf)
