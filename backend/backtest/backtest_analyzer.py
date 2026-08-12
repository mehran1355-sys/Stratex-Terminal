"""
تحلیل نتایج بک‌تست
Backtest Analyzer Module
"""

import logging
from typing import Dict, List
import numpy as np
from .backtest_engine import BacktestResult

logger = logging.getLogger(__name__)


class BacktestAnalyzer:
    @staticmethod
    def generate_summary(result: BacktestResult) -> Dict:
        return {
            "overview": {
                "symbol": result.config.symbol,
                "timeframe": result.config.timeframe,
                "period": f"{result.config.start_date.date()} تا {result.config.end_date.date()}",
                "initial_balance": result.config.initial_balance,
                "final_balance": round(result.config.initial_balance + result.total_pnl, 2),
                "total_return": f"{result.total_pnl_pct:.2f}%",
            },
            "performance": {
                "total_trades": result.total_trades,
                "winning_trades": result.winning_trades,
                "losing_trades": result.losing_trades,
                "win_rate": f"{result.win_rate:.1f}%",
                "profit_factor": f"{result.profit_factor:.2f}",
                "sharpe_ratio": f"{result.sharpe_ratio:.2f}",
                "max_drawdown": f"${result.max_drawdown:.2f} ({result.max_drawdown_pct:.2f}%)",
            },
            "trade_details": {
                "avg_win": f"${result.avg_win:.2f}",
                "avg_loss": f"${result.avg_loss:.2f}",
                "largest_win": f"${result.largest_win:.2f}",
                "largest_loss": f"${result.largest_loss:.2f}",
                "avg_duration": str(result.avg_trade_duration),
            },
            "signals": {
                "generated": result.signals_generated,
                "taken": result.signals_taken,
                "cancelled": result.signals_cancelled,
                "signal_quality": f"{(result.signals_taken / result.signals_generated * 100):.1f}%" if result.signals_generated > 0 else "0%",
            },
            "break_types": {
                "initial_break": result.initial_break_trades,
                "complete_break": result.complete_break_trades,
            },
        }

    @staticmethod
    def analyze_by_month(result: BacktestResult) -> List[Dict]:
        monthly = []
        for month, pnl in result.monthly_returns.items():
            monthly.append({"month": month, "pnl": round(pnl, 2)})
        return sorted(monthly, key=lambda x: x["month"])

    @staticmethod
    def analyze_win_loss_streaks(result: BacktestResult) -> Dict:
        streaks = []
        current_streak = 0
        current_type = None
        for t in result.trades:
            if t.pnl > 0:
                if current_type == "WIN":
                    current_streak += 1
                else:
                    if current_streak > 0:
                        streaks.append({"type": current_type, "length": current_streak})
                    current_streak = 1
                    current_type = "WIN"
            else:
                if current_type == "LOSS":
                    current_streak += 1
                else:
                    if current_streak > 0:
                        streaks.append({"type": current_type, "length": current_streak})
                    current_streak = 1
                    current_type = "LOSS"
        if current_streak > 0:
            streaks.append({"type": current_type, "length": current_streak})
        win_streaks = [s["length"] for s in streaks if s["type"] == "WIN"]
        loss_streaks = [s["length"] for s in streaks if s["type"] == "LOSS"]
        return {
            "max_win_streak": max(win_streaks) if win_streaks else 0,
            "max_loss_streak": max(loss_streaks) if loss_streaks else 0,
            "all_streaks": streaks,
        }
