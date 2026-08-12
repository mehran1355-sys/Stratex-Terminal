"""
اجرای معاملات و مدیریت پوزیشن‌ها
Trade Executor Module
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

from strategy_engine import TradeSignal, TradeStatus, BreakType
from mt5_connector import MT5Connector
from risk_manager import RiskManager
from lot_manager import LotManager, SymbolClassifier


class OrderType(Enum):
    BUY_LIMIT = "BUY_LIMIT"
    SELL_LIMIT = "SELL_LIMIT"


class ExecutionMode(Enum):
    AUTO = "اتوماتیک"
    SEMI_AUTO = "نیمه_اتوماتیک"
    MANUAL = "دستی"


class TradeExecutor:
    def __init__(self, mt5_connector: MT5Connector, risk_manager: RiskManager, lot_manager: LotManager = None, execution_mode: ExecutionMode = ExecutionMode.SEMI_AUTO):
        self.mt5 = mt5_connector
        self.risk_manager = risk_manager
        self.lot_manager = lot_manager or LotManager()
        self.execution_mode = execution_mode
        self.active_positions: Dict[str, Dict] = {}
        self.pending_orders: Dict[int, Dict] = {}
        self.order_history: List[Dict] = []

    def get_optimal_lot(self, symbol: str, use_risk: bool = False, stop_loss_pips: float = 0) -> float:
        default_lot = self.lot_manager.get_lot_for_symbol(symbol)
        if use_risk and stop_loss_pips > 0:
            account = self.mt5.get_account_info()
            balance = account.get("balance", 10000)
            risk_pct = self.risk_manager.config.max_risk_per_trade_pct * 100
            calculated = self.lot_manager.calculate_lot_by_risk(symbol, balance, risk_pct, stop_loss_pips)
            config = self.lot_manager.get_lot_config_for_symbol(symbol)
            return min(calculated, config.max_lot)
        return default_lot

    def place_entry_orders_from_plan(self, signal: TradeSignal, use_risk_lot: bool = False, user_confirmed: bool = True) -> Dict:
        if self.execution_mode == ExecutionMode.MANUAL:
            return {}
        if self.execution_mode == ExecutionMode.SEMI_AUTO and not user_confirmed:
            logger.info("Waiting for user confirmation")
            return {}

        all_orders = {"middle": [], "far": [], "total_orders": 0, "total_volume": 0.0}
        order_type = OrderType.BUY_LIMIT if signal.pattern_direction == "صعودی" else OrderType.SELL_LIMIT

        optimal_lot = self.get_optimal_lot(signal.symbol, use_risk_lot)
        signal.total_volume = optimal_lot

        for zone_name in ["middle", "far"]:
            entries = signal.entry_plan.get(zone_name, [])
            for entry in entries:
                entry_volume = optimal_lot * (entry["percentage"] / 100)
                ticket = self.mt5.send_order(signal.symbol, order_type.value, entry_volume, entry["price"], signal.sl, 0, f"SND_{signal.timeframe}_{zone_name}_{entry['zone_part']}")
                if ticket:
                    order_info = {"ticket": ticket, "price": entry["price"], "volume": entry_volume, "zone": zone_name, "zone_part": entry["zone_part"], "type": order_type.value, "symbol": signal.symbol, "created_at": datetime.now()}
                    all_orders[zone_name].append(order_info)
                    all_orders["total_orders"] += 1
                    all_orders["total_volume"] += entry_volume
                    self.pending_orders[ticket] = order_info
                    logger.info(f"✅ Order: {signal.symbol} | {zone_name} | {entry['price']:.5f} | {entry_volume:.4f} | Ticket: {ticket}")
        return all_orders

    def manage_positions(self, signal: TradeSignal, current_price: float):
        if not signal.tp1_already_hit:
            if (signal.pattern_direction == "صعودی" and current_price >= signal.tp1) or (signal.pattern_direction == "نزولی" and current_price <= signal.tp1):
                self._close_50_percent(signal)
                signal.tp1_already_hit = True
                logger.info(f"🎯 TP1 hit for {signal.symbol}")
        if (signal.pattern_direction == "صعودی" and current_price >= signal.tp2) or (signal.pattern_direction == "نزولی" and current_price <= signal.tp2):
            self._close_remaining(signal)
            signal.status = TradeStatus.TP2_HIT
        if (signal.pattern_direction == "صعودی" and current_price <= signal.sl) or (signal.pattern_direction == "نزولی" and current_price >= signal.sl):
            self._close_all(signal)
            signal.status = TradeStatus.SL_HIT

    def _close_50_percent(self, signal: TradeSignal):
        total_volume = signal.total_volume
        volume_to_close = total_volume * 0.5
        closed = 0
        for ticket, order in list(self.pending_orders.items()):
            if order.get("symbol") != signal.symbol:
                continue
            if closed >= volume_to_close:
                break
            if order["volume"] <= (volume_to_close - closed):
                self.mt5.close_position(ticket)
                closed += order["volume"]
                del self.pending_orders[ticket]
        logger.info(f"Closed 50%: {closed:.4f}")

    def _close_remaining(self, signal: TradeSignal):
        for ticket, order in list(self.pending_orders.items()):
            if order.get("symbol") == signal.symbol:
                self.mt5.close_position(ticket)
                del self.pending_orders[ticket]

    def _close_all(self, signal: TradeSignal):
        self._close_remaining(signal)

    def close_positions_at_timeframe_end(self, timeframe: str):
        to_close = [t for t, o in self.pending_orders.items() if o.get("timeframe") == timeframe]
        for ticket in to_close:
            self.mt5.close_position(ticket)
            if ticket in self.pending_orders:
                del self.pending_orders[ticket]
        logger.info(f"Closed {len(to_close)} positions at {timeframe} end")

    def set_execution_mode(self, mode: ExecutionMode):
        self.execution_mode = mode

    def get_active_positions_summary(self) -> List[Dict]:
        return [{"ticket": t, "symbol": o.get("symbol"), "type": o.get("type"), "volume": o.get("volume"), "price": o.get("price")} for t, o in self.pending_orders.items()]

    def get_active_positions_count(self) -> int:
        return len(self.pending_orders)


class SemiAutoTradeManager:
    def __init__(self, executor: TradeExecutor):
        self.executor = executor
        self.pending_approvals: Dict[str, TradeSignal] = {}

    def request_approval(self, signal: TradeSignal) -> str:
        approval_id = f"APPROVE_{signal.symbol}_{signal.timeframe}_{datetime.now().timestamp()}"
        self.pending_approvals[approval_id] = signal
        logger.info(f"Approval requested: {approval_id} | {signal.symbol} | TP1:{signal.tp1:.5f} TP2:{signal.tp2:.5f} SL:{signal.sl:.5f}")
        return approval_id

    def approve(self, approval_id: str) -> bool:
        if approval_id in self.pending_approvals:
            signal = self.pending_approvals.pop(approval_id)
            self.executor.place_entry_orders_from_plan(signal, user_confirmed=True)
            return True
        return False

    def reject(self, approval_id: str, reason: str = ""):
        if approval_id in self.pending_approvals:
            self.pending_approvals.pop(approval_id)
            logger.info(f"Rejected: {approval_id} - {reason}")
