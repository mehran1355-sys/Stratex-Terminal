"""
سرور اصلی FastAPI
Main API Server
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from strategy_engine import StrategyEngine, MarketMonitor
from mt5_connector import MT5Connector
from risk_manager import RiskManager, RiskConfig
from trade_executor import TradeExecutor, ExecutionMode, SemiAutoTradeManager
from lot_manager import LotManager, SymbolClassifier, AssetType
from market_selector import MarketSelector, MarketType, TradingStyle, StrategyRegistry
from telegram_service import TelegramService, TelegramConfig
from excel_reporter import ExcelReporter
from chart_service import ChartService
from voice_service import VoiceService, VoiceConfig
from server_registry import ServerRegistry

logger = logging.getLogger(__name__)

app = FastAPI(title="Stratex Algo Bot", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Services
mt5 = MT5Connector()
risk_mgr = RiskManager()
lot_mgr = LotManager()
market_sel = MarketSelector()
strategy_eng = StrategyEngine()
trade_exec = TradeExecutor(mt5, risk_mgr, lot_mgr)
chart_svc = ChartService()
excel_reporter = ExcelReporter()
server_registry = ServerRegistry()
voice_svc = VoiceService()

telegram = None
config_path = Path("config.json")
if config_path.exists():
    with open(config_path) as f:
        cfg = json.load(f)
    if cfg.get("telegram_bot_token"):
        telegram = TelegramService(TelegramConfig(cfg["telegram_bot_token"], cfg.get("telegram_channel_id", ""), cfg.get("admin_chat_ids", [])))

semi_auto = SemiAutoTradeManager(trade_exec)


@app.get("/health")
async def health():
    return {"status": "healthy", "mt5": mt5.connected, "timestamp": datetime.now().isoformat()}


@app.get("/api/symbols/list")
async def symbols_list():
    return {"symbols": ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "XAUUSD"]}


@app.post("/api/symbols/add")
async def symbols_add(data: Dict):
    return {"success": True, "symbol": data.get("symbols", [""])[0]}


@app.post("/api/analysis/run")
async def analysis_run(data: Dict):
    symbol = data.get("symbol", "EURUSD")
    tf = data.get("timeframe", "daily")
    volume = data.get("volume", 0.01)
    monitor_tf = MarketMonitor.get_monitoring_timeframe(tf)
    multi_tf = mt5.get_multi_timeframe_data(symbol, [tf, monitor_tf])
    signal = strategy_eng.analyze(symbol, multi_tf, tf, volume)
    if not signal:
        return {"success": False, "message": "No signal"}
    return {"success": True, "signal": {"symbol": symbol, "timeframe": tf, "direction": signal.pattern_direction, "break_type": signal.break_type.value, "entry_plan": signal.entry_plan, "tp1": signal.tp1, "tp2": signal.tp2, "sl": signal.sl, "volume": signal.total_volume, "status": signal.status.value}}


@app.post("/api/analysis/batch")
async def analysis_batch(data: Dict):
    symbols = data.get("symbols", ["EURUSD"])
    results = []
    for s in symbols:
        r = await analysis_run({"symbol": s, "timeframe": "daily"})
        results.append(r)
    return {"success": True, "results": results}


@app.get("/api/trades/active")
async def trades_active():
    return {"active_trades": trade_exec.get_active_positions_summary()}


@app.get("/api/reports/daily")
async def report_daily():
    return {"statistics": risk_mgr.get_daily_statistics()}


@app.get("/api/lot/settings")
async def lot_settings():
    return {"settings": lot_mgr.get_all_lot_settings()}


@app.post("/api/lot/set")
async def lot_set(data: Dict):
    at = data.get("asset_type", "forex_pairs")
    lot = data.get("default_lot", 0.10)
    return {"success": True}


@app.get("/api/market/status")
async def market_status():
    return {"markets": market_sel.get_supported_markets(), "styles": market_sel.get_supported_styles()}


@app.post("/api/market/select")
async def market_select(data: Dict):
    m = {"forex": MarketType.FOREX}.get(data.get("market", "forex"), MarketType.FOREX)
    return market_sel.set_market(data.get("user_id", "default"), m)


@app.post("/api/market/style")
async def market_style(data: Dict):
    s = {"mid_term": TradingStyle.MID_TERM}.get(data.get("style", "mid_term"), TradingStyle.MID_TERM)
    return market_sel.set_trading_style(data.get("user_id", "default"), s)


@app.post("/api/backtest/run")
async def backtest_run(data: Dict):
    return {"success": True, "summary": {"overview": {}, "performance": {}}}


@app.get("/api/backtest/timeframes")
async def backtest_timeframes():
    return {"timeframes": ["monthly","weekly","daily","12h","8h","6h","4h","2h","1h","30m","15m","10m","5m","3m","2m","1m"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
