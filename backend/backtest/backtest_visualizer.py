"""
نمودارهای بک‌تست
Backtest Visualizer Module
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from typing import Dict, List
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.family'] = 'sans-serif'


class BacktestVisualizer:
    COLORS = {"profit": "#00C853", "loss": "#FF1744", "equity": "#2196F3", "balance": "#FF9800", "drawdown": "#F44336", "background": "#1a1a2e"}

    @classmethod
    def plot_equity_curve(cls, equity_data: List[Dict]) -> bytes:
        fig, ax = plt.subplots(figsize=(14, 7), facecolor=cls.COLORS["background"])
        ax.set_facecolor(cls.COLORS["background"])
        times = [datetime.fromisoformat(d['time']) for d in equity_data]
        equity = [d['equity'] for d in equity_data]
        balance = [d['balance'] for d in equity_data]
        ax.plot(times, equity, color=cls.COLORS["equity"], linewidth=2, label='Equity')
        ax.plot(times, balance, color=cls.COLORS["balance"], linewidth=1, alpha=0.7, label='Balance')
        peak = np.maximum.accumulate(equity)
        drawdown = np.array(equity) - peak
        ax.fill_between(times, equity, peak, where=(drawdown < 0), color=cls.COLORS["drawdown"], alpha=0.3, label='Drawdown')
        ax.set_title('📈 Equity Curve', color='white', fontsize=14)
        ax.set_xlabel('تاریخ', color='white')
        ax.set_ylabel('موجودی ($)', color='white')
        ax.legend()
        ax.grid(True, alpha=0.2)
        ax.tick_params(colors='white')
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        return buf.read()

    @classmethod
    def plot_monthly_returns(cls, monthly_data: List[Dict]) -> bytes:
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=cls.COLORS["background"])
        ax.set_facecolor(cls.COLORS["background"])
        months = [d['month'] for d in monthly_data]
        returns = [d['pnl'] for d in monthly_data]
        colors = [cls.COLORS["profit"] if r >= 0 else cls.COLORS["loss"] for r in returns]
        ax.bar(months, returns, color=colors, alpha=0.8)
        ax.axhline(y=0, color='white', linewidth=1, alpha=0.5)
        ax.set_title('📊 بازدهی ماهانه', color='white', fontsize=14)
        ax.set_xlabel('ماه', color='white')
        ax.set_ylabel('سود/ضرر ($)', color='white')
        ax.tick_params(colors='white', rotation=45)
        ax.grid(True, alpha=0.2, axis='y')
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        return buf.read()
