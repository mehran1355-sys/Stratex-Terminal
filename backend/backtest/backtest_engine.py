"""
موتور اصلی بک‌تست
Backtest Engine Module
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

logger = logging.getLogger(__name__)

import sys
sys.path.append('..')
from strategy_engine import (
    Candle, CandleSize, CandleDirection, BreakType, TradeStatus,
    CandleSizeCalculator, OrangeLineDrawer, PurpleLineCalculator,
    MarketMonitor, TradeSignalBuilder, TradeValidator, EntryPlanBuilder,
    OrangeLines
)


class BacktestMode(Enum):
    ALL_TICKS = "همه_تیک‌ها"
    OHLC = "قیمت_باز_و_بسته"
    CLOSE_ONLY = "فقط_قیمت_بسته"


@dataclass
class BacktestConfig:
    symbol: str
    timeframe: str
    monitor_timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10000.0
    total_volume: float = 0.10
    split_count: int = 2
    mode: BacktestMode = BacktestMode.OHLC
    commission_per_lot: float = 0.0
    spread_pips: float = 1.0
    enable_tp1_partial: bool = True
    use_risk_management: bool = True
    max_risk_pct: float = 2.0


@dataclass
class BacktestTrade:
    trade_id: int
    symbol: str
    direction: str
    entry_time: datetime
    entry_price: float
    volume: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: str = ""
    pnl: float = 0.0
    pnl_pct: float = 0.0
    partial_close_time: Optional[datetime] = None
    partial_close_price: Optional[float] = None
    partial_pnl: float = 0.0


@dataclass
class BacktestResult:
    config: BacktestConfig
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    largest_win: float = 0.0
    largest_loss: float = 0.0
    avg_trade_duration: timedelta = field(default_factory=timedelta)
    trades: List[BacktestTrade] = field(default_factory=list)
    equity_curve: List[Dict] = field(default_factory=list)
    monthly_returns: Dict[str, float] = field(default_factory=dict)
    signals_generated: int = 0
    signals_taken: int = 0
    signals_cancelled: int = 0
    initial_break_trades: int = 0
    complete_break_trades: int = 0


SUPPORTED_TIMEFRAMES = {
    "monthly": "ماهیانه", "weekly": "هفتگی", "daily": "روزانه",
    "12h": "۱۲ ساعته", "8h": "۸ ساعته", "6h": "۶ ساعته",
    "4h": "۴ ساعته", "2h": "۲ ساعته", "1h": "۱ ساعته",
    "30m": "۳۰ دقیقه", "15m": "۱۵ دقیقه", "10m": "۱۰ دقیقه",
    "5m": "۵ دقیقه", "3m": "۳ دقیقه", "2m": "۲ دقیقه", "1m": "۱ دقیقه",
}


class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Dict] = []
        self.current_balance: float = config.initial_balance
        self.trade_counter: int = 0
        self.open_positions: Dict[int, BacktestTrade] = {}

    def run(self, analysis_candles: List[Candle], monitor_candles: List[Candle], progress_callback=None) -> BacktestResult:
        signals_generated = signals_taken = signals_cancelled = 0
        initial_break_count = complete_break_count = 0
        analysis_window = 30

        for i in range(analysis_window, len(monitor_candles) - 1):
            current_monitor = monitor_candles[i]
            current_time = current_monitor.time

            self._check_timeframe_end(current_time, current_monitor)
            self._manage_open_positions(current_monitor)

            if self._should_generate_signal(i, monitor_candles, current_time):
                signal_data = self._generate_signal(analysis_candles, monitor_candles, i)
                if signal_data:
                    signals_generated += 1
                    valid, reason = TradeValidator.check_cancellation_rules(
                        signal_data['signal'], monitor_candles[:i+1], monitor_candles[i].close
                    )
                    if not valid:
                        signals_cancelled += 1
                        continue
                    trade = self._open_trade(signal_data, current_monitor)
                    if trade:
                        signals_taken += 1
                        self.trades.append(trade)
                        self.open_positions[trade.trade_id] = trade
                        if signal_data['break_type'] == BreakType.INITIAL:
                            initial_break_count += 1
                        else:
                            complete_break_count += 1

            self._record_equity(current_time, current_monitor.close)

        # Close remaining trades
        if monitor_candles:
            final_candle = monitor_candles[-1]
            for tid in list(self.open_positions.keys()):
                self._close_trade(tid, final_candle.close, final_candle.time, "END_OF_TEST")

        return self._calculate_results(signals_generated, signals_taken, signals_cancelled,
                                       initial_break_count, complete_break_count)

    def _should_generate_signal(self, index, monitor_candles, current_time):
        tf = self.config.timeframe
        if index == 0:
            return True
        prev = monitor_candles[index-1].time
        if tf == "daily":
            return current_time.day != prev.day
        if tf == "weekly":
            return current_time.isocalendar()[1] != prev.isocalendar()[1]
        if tf == "monthly":
            return current_time.month != prev.month
        return True

    def _generate_signal(self, analysis_candles, monitor_candles, idx):
        try:
            window = analysis_candles[:idx+1]
            if len(window) < 2:
                return None
            candle_size, _ = CandleSizeCalculator.calculate(window, self.config.timeframe)
            orange = OrangeLineDrawer.draw(window[-1], candle_size, self.config.timeframe)
            multi_tf = {self.config.timeframe: window, self.config.monitor_timeframe: monitor_candles[:idx+1]}
            purple = PurpleLineCalculator.calculate_purple_lines(multi_tf, self.config.timeframe, orange)
            monitor_result = MarketMonitor.evaluate(monitor_candles[:idx+1], orange)
            if monitor_result["break_type"] == BreakType.NONE:
                return None
            signal = TradeSignalBuilder.build(self.config.symbol, self.config.timeframe, orange, purple,
                                              monitor_result, self.config.total_volume, self.config.split_count)
            if signal:
                return {'signal': signal, 'orange': orange, 'purple': purple,
                        'break_type': monitor_result['break_type'],
                        'direction': monitor_result['pattern_direction']}
        except Exception as e:
            logger.error(f"Signal error: {e}")
        return None

    def _open_trade(self, signal_data, candle):
        direction = signal_data['direction']
        signal = signal_data['signal']
        spread = self.config.spread_pips * 0.0001
        entry_price = candle.close + spread if direction == "صعودی" else candle.close - spread
        self.trade_counter += 1
        trade = BacktestTrade(
            trade_id=self.trade_counter, symbol=self.config.symbol,
            direction="BUY" if direction == "صعودی" else "SELL",
            entry_time=candle.time or datetime.now(), entry_price=entry_price,
            volume=self.config.total_volume,
            stop_loss=signal.sl, take_profit_1=signal.tp1, take_profit_2=signal.tp2,
        )
        return trade

    def _manage_open_positions(self, candle):
        for tid in list(self.open_positions.keys()):
            t = self.open_positions[tid]
            high, low, close = candle.high, candle.low, candle.close
            if t.direction == "BUY":
                if high >= t.take_profit_2:
                    self._close_trade(tid, t.take_profit_2, candle.time, "TP2")
                elif not t.partial_close_time and high >= t.take_profit_1:
                    if self.config.enable_tp1_partial:
                        self._partial_close(tid, t.take_profit_1, candle.time)
                elif low <= t.stop_loss:
                    self._close_trade(tid, t.stop_loss, candle.time, "SL")
            else:
                if low <= t.take_profit_2:
                    self._close_trade(tid, t.take_profit_2, candle.time, "TP2")
                elif not t.partial_close_time and low <= t.take_profit_1:
                    if self.config.enable_tp1_partial:
                        self._partial_close(tid, t.take_profit_1, candle.time)
                elif high >= t.stop_loss:
                    self._close_trade(tid, t.stop_loss, candle.time, "SL")

    def _close_trade(self, tid, price, time, reason):
        t = self.open_positions.pop(tid, None)
        if not t: return
        t.exit_price, t.exit_time, t.exit_reason = price, time, reason
        pnl = ((price - t.entry_price) if t.direction == "BUY" else (t.entry_price - price)) * t.volume * 100000
        pnl += t.partial_pnl - self.config.commission_per_lot * t.volume * 2
        t.pnl = round(pnl, 2)
        t.pnl_pct = round(pnl / self.config.initial_balance * 100, 2)
        self.current_balance += pnl

    def _partial_close(self, tid, price, time):
        t = self.open_positions.get(tid)
        if not t: return
        t.partial_close_time, t.partial_close_price = time, price
        half_vol = t.volume / 2
        pnl = ((price - t.entry_price) if t.direction == "BUY" else (t.entry_price - price)) * half_vol * 100000
        t.partial_pnl = round(pnl, 2)

    def _check_timeframe_end(self, current_time, candle):
        for tid in list(self.open_positions.keys()):
            t = self.open_positions[tid]
            if t.entry_time and (current_time - t.entry_time).days >= 1:
                self._close_trade(tid, candle.close, current_time, "TIMEFRAME_END")

    def _record_equity(self, time, price):
        floating = 0
        for t in self.open_positions.values():
            floating += ((price - t.entry_price) if t.direction == "BUY" else (t.entry_price - price)) * t.volume * 100000
        self.equity_curve.append({
            'time': time.isoformat() if time else '',
            'balance': round(self.current_balance, 2),
            'equity': round(self.current_balance + floating, 2),
            'floating_pnl': round(floating, 2),
            'open_positions': len(self.open_positions),
        })

    def _calculate_results(self, generated, taken, cancelled, initial_count, complete_count):
        result = BacktestResult(config=self.config, trades=self.trades, equity_curve=self.equity_curve,
                                signals_generated=generated, signals_taken=taken, signals_cancelled=cancelled,
                                initial_break_trades=initial_count, complete_break_trades=complete_count)
        if not self.trades:
            return result
        result.total_trades = len(self.trades)
        result.winning_trades = sum(1 for t in self.trades if t.pnl > 0)
        result.losing_trades = sum(1 for t in self.trades if t.pnl < 0)
        result.win_rate = result.winning_trades / result.total_trades * 100
        result.total_pnl = sum(t.pnl for t in self.trades)
        result.total_pnl_pct = result.total_pnl / self.config.initial_balance * 100
        wins = [t.pnl for t in self.trades if t.pnl > 0]
        losses = [t.pnl for t in self.trades if t.pnl < 0]
        result.avg_win = np.mean(wins) if wins else 0
        result.avg_loss = abs(np.mean(losses)) if losses else 0
        result.largest_win = max(wins) if wins else 0
        result.largest_loss = min(losses) if losses else 0
        gross_profit = sum(wins)
        gross_loss = abs(sum(losses))
        result.profit_factor = gross_profit / gross_loss if gross_loss else float('inf')
        if len(self.equity_curve) > 1:
            returns = []
            for i in range(1, len(self.equity_curve)):
                prev = self.equity_curve[i-1]['equity']
                curr = self.equity_curve[i]['equity']
                if prev > 0:
                    returns.append((curr - prev) / prev)
            if returns and np.std(returns) > 0:
                result.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        if self.equity_curve:
            peak = self.equity_curve[0]['equity']
            max_dd = 0
            for point in self.equity_curve:
                eq = point['equity']
                if eq > peak: peak = eq
                dd = peak - eq
                if dd > max_dd: max_dd = dd
            result.max_drawdown = max_dd
            result.max_drawdown_pct = (max_dd / peak * 100) if peak else 0
        return result
