"""
مدل‌های دیتابیس
Database Models
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from .connection import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255))
    password_hash = Column(String(255))
    role = Column(String(20), default="viewer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    trade_id = Column(String(50), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20))
    direction = Column(String(10))
    entry_price = Column(Float)
    exit_price = Column(Float)
    stop_loss = Column(Float)
    take_profit_1 = Column(Float)
    take_profit_2 = Column(Float)
    total_volume = Column(Float)
    pnl = Column(Float, default=0)
    status = Column(String(20), default="pending")
    entry_time = Column(DateTime)
    exit_time = Column(DateTime)
    exit_reason = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True)
    signal_id = Column(String(50), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20))
    timeframe = Column(String(20))
    direction = Column(String(10))
    break_type = Column(String(20))
    tp1 = Column(Float)
    tp2 = Column(Float)
    sl = Column(Float)
    volume = Column(Float)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemConfig(Base):
    __tablename__ = "system_configs"
    id = Column(Integer, primary_key=True)
    config_key = Column(String(100), unique=True)
    config_value = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(50))
    action = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(50))
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class EquitySnapshot(Base):
    __tablename__ = "equity_snapshots"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime)
    balance = Column(Float)
    equity = Column(Float)
    daily_pnl = Column(Float)


class BacktestResult(Base):
    __tablename__ = "backtest_results"
    id = Column(Integer, primary_key=True)
    backtest_id = Column(String(50), unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    symbol = Column(String(20))
    timeframe = Column(String(20))
    total_trades = Column(Integer)
    win_rate = Column(Float)
    total_pnl = Column(Float)
    profit_factor = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    config_json = Column(JSON)
    trades_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
