#!/usr/bin/env python3
"""Health Check Script"""

import sys
from datetime import datetime
from typing import List, Tuple

GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


def main():
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}  🏥 Health Check{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")
    print(f"  زمان: {datetime.now():%Y-%m-%d %H:%M:%S}")

    results: List[Tuple[str, bool]] = []

    try:
        from strategy_engine import StrategyEngine, Candle
        results.append(("Strategy Engine", True))
    except Exception:
        results.append(("Strategy Engine", False))

    try:
        from mt5_connector import MT5Connector
        results.append(("MT5 Connector", True))
    except:
        results.append(("MT5 Connector", False))

    try:
        from risk_manager import RiskManager
        results.append(("Risk Manager", True))
    except:
        results.append(("Risk Manager", False))

    try:
        from lot_manager import LotManager
        results.append(("Lot Manager", True))
    except:
        results.append(("Lot Manager", False))

    try:
        from market_selector import MarketSelector
        results.append(("Market Selector", True))
    except:
        results.append(("Market Selector", False))

    try:
        from trade_executor import TradeExecutor
        results.append(("Trade Executor", True))
    except:
        results.append(("Trade Executor", False))

    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    total = len(results)
    passed = sum(1 for _, ok in results if ok)
    failed = total - passed
    print(f"{BOLD}  مجموع: {total} | {GREEN}پاس: {passed}{RESET} | {RED}خطا: {failed}{RESET}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
