"""
سرویس رسم نمودار
Chart Service Module
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['figure.figsize'] = (16, 9)


class ChartService:
    COLORS = {"orange": "#FF8C00", "purple": "#800080", "green": "#00C853", "red": "#FF1744", "background": "#1a1a2e"}

    def __init__(self, dark_mode: bool = True):
        self.dark_mode = dark_mode
        if dark_mode:
            plt.style.use('dark_background')

    def draw_analysis_chart(self, candles: List[Dict], orange_upper: float, orange_lower: float, purple_upper: float = None, purple_lower: float = None, entry_zones: Dict = None, symbol: str = "", timeframe: str = "", pattern_direction: str = "") -> bytes:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        self._draw_candlesticks(ax1, candles)
        ax1.axhline(y=orange_upper, color=self.COLORS["orange"], linewidth=2, linestyle='-', label='نارنجی بالا', alpha=0.8)
        ax1.axhline(y=orange_lower, color=self.COLORS["orange"], linewidth=2, linestyle='-', label='نارنجی پایین', alpha=0.8)
        ax1.fill_between([0, len(candles)-1], orange_lower, orange_upper, alpha=0.1, color='orange', label='منطقه احتیاط')
        zone_h = orange_upper - orange_lower
        for div_y in [orange_lower + zone_h/3, orange_lower + 2*zone_h/3]:
            ax1.axhline(y=div_y, color="gray", linewidth=1, linestyle='--', alpha=0.5)
        if purple_upper:
            ax1.axhline(y=purple_upper, color=self.COLORS["purple"], linewidth=2, linestyle='-', label='TP2', alpha=0.8)
        if purple_lower:
            ax1.axhline(y=purple_lower, color=self.COLORS["purple"], linewidth=2, linestyle='-', label='SL', alpha=0.8)
        ax1.set_title(f'{symbol} - {timeframe} - {pattern_direction}', fontsize=14, fontweight='bold')
        ax1.set_ylabel('قیمت')
        ax1.legend(loc='upper left', fontsize=8)
        ax1.grid(True, alpha=0.3)
        volumes = [c.get("volume", 0) for c in candles]
        colors = [self.COLORS["green"] if c.get("close", 0) >= c.get("open", 0) else self.COLORS["red"] for c in candles]
        ax2.bar(range(len(volumes)), volumes, color=colors, alpha=0.6, width=0.8)
        ax2.set_ylabel('حجم')
        ax2.grid(True, alpha=0.3)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor())
        buf.seek(0)
        plt.close(fig)
        return buf.read()

    def _draw_candlesticks(self, ax, candles: List[Dict]):
        for i, c in enumerate(candles):
            o, h, l, cl = c.get("open", 0), c.get("high", 0), c.get("low", 0), c.get("close", 0)
            color = self.COLORS["green"] if cl >= o else self.COLORS["red"]
            body_bottom = o if cl >= o else cl
            body_height = abs(cl - o)
            if body_height > 0:
                ax.add_patch(Rectangle((i-0.4, body_bottom), 0.8, body_height, facecolor=color, edgecolor=color, alpha=0.9))
            else:
                ax.plot([i-0.4, i+0.4], [cl, cl], color=color, linewidth=1.5)
            ax.plot([i, i], [l, h], color=color, linewidth=1, alpha=0.8)

    def draw_equity_curve(self, equity_data: List[Dict], title: str = "Equity Curve") -> bytes:
        fig, ax = plt.subplots(figsize=(16, 6))
        dates = [d.get("date", "") for d in equity_data]
        balances = [d.get("balance", 0) for d in equity_data]
        ax.plot(dates, balances, color=self.COLORS["green"], linewidth=2, marker='o', markersize=3)
        ax.set_title(f'📈 {title}', fontsize=14, fontweight='bold')
        ax.set_xlabel('تاریخ')
        ax.set_ylabel('موجودی')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf.read()
