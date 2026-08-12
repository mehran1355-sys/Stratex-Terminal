"""
مدیریت ریسک و محاسبات حجم
Risk Manager Module
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Callable

logger = logging.getLogger(__name__)


@dataclass
class RiskConfig:
    max_portfolio_risk_pct: float = 0.40
    max_risk_per_trade_pct: float = 0.02
    risk_reward_ratio: float = 2.0
    ask_user_on_limit_exceeded: bool = True
    max_concurrent_trades: int = 5
    max_daily_loss_pct: float = 0.05


@dataclass
class PositionSizing:
    total_volume: float
    volume_per_entry: Dict[str, float]
    risk_amount: float
    potential_profit: float


class RiskManager:
    def __init__(self, config: RiskConfig = None):
        self.config = config or RiskConfig()
        self.active_trades: Dict[str, Dict] = {}
        self.daily_pnl: float = 0.0
        self.total_trades_today: int = 0

    def set_max_portfolio_risk(self, percentage: float):
        if 1 < percentage <= 100:
            percentage = percentage / 100.0
        if 0 < percentage <= 1.0:
            self.config.max_portfolio_risk_pct = percentage
            logger.info(f"Max portfolio risk set to {percentage*100:.1f}%")

    def set_max_risk_per_trade(self, percentage: float):
        if 1 < percentage <= 100:
            percentage = percentage / 100.0
        if 0 < percentage <= 0.10:
            self.config.max_risk_per_trade_pct = percentage

    def calculate_position_size(self, account_balance: float, entry_price: float, stop_loss: float, total_volume: float = None) -> PositionSizing:
        if total_volume is None:
            risk_amount = account_balance * self.config.max_risk_per_trade_pct
            sl_distance = abs(entry_price - stop_loss)
            total_volume = risk_amount / sl_distance if sl_distance > 0 else 0.01
        risk_amount = total_volume * abs(entry_price - stop_loss)
        potential_profit = risk_amount * self.config.risk_reward_ratio
        return PositionSizing(total_volume=round(total_volume, 4), volume_per_entry={"entry": round(total_volume, 4)}, risk_amount=round(risk_amount, 2), potential_profit=round(potential_profit, 2))

    def calculate_split_volume(self, total_volume: float, break_type: str, split_ratios: List[float] = None) -> Dict[str, float]:
        if break_type == "initial":
            return {"far": total_volume}
        elif break_type == "complete":
            return {"middle": total_volume * 0.5, "far": total_volume * 0.5}
        return {}

    def validate_trade(self, account_balance: float, account_equity: float, current_margin_used: float, new_trade_margin: float, confirm_callback: Callable = None) -> Tuple[bool, str]:
        if account_balance <= 0:
            return False, "❌ موجودی ناکافی"
        projected_margin = current_margin_used + new_trade_margin
        margin_ratio = projected_margin / account_balance
        if margin_ratio > self.config.max_portfolio_risk_pct:
            msg = f"⚠️ ریسک {margin_ratio*100:.1f}% از حد {self.config.max_portfolio_risk_pct*100:.1f}% فراتر است"
            if self.config.ask_user_on_limit_exceeded and confirm_callback:
                if confirm_callback(msg):
                    return True, "✅ تأیید شد"
                return False, "❌ رد شد"
            return False, msg
        if len(self.active_trades) >= self.config.max_concurrent_trades:
            return False, f"❌ حداکثر {self.config.max_concurrent_trades} معامله همزمان"
        if self.daily_pnl < -(account_balance * self.config.max_daily_loss_pct):
            return False, f"❌ حد ضرر روزانه"
        return True, "✅ مجاز"

    def add_trade(self, trade_id: str, trade_info: Dict):
        self.active_trades[trade_id] = trade_info
        self.total_trades_today += 1

    def remove_trade(self, trade_id: str, pnl: float = 0):
        if trade_id in self.active_trades:
            del self.active_trades[trade_id]
            self.daily_pnl += pnl

    def get_daily_statistics(self) -> Dict:
        return {"active_trades": len(self.active_trades), "total_trades_today": self.total_trades_today, "daily_pnl": round(self.daily_pnl, 2)}

    @staticmethod
    def calculate_pnl(entry_price: float, exit_price: float, volume: float, direction: str) -> float:
        if direction.lower() == "buy":
            return round((exit_price - entry_price) * volume * 100000, 2)
        else:
            return round((entry_price - exit_price) * volume * 100000, 2)
