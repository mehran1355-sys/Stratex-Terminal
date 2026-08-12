"""
لاگ حسابرسی امنیتی
"""

import logging
import json
from datetime import datetime
from pathlib import Path
import threading

logger = logging.getLogger(__name__)


class AuditLogger:
    def __init__(self, log_file: str = "logs/audit.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def log(self, event_type: str, user_id: str = "anonymous", action: str = "", details: dict = None, ip_address: str = "", success: bool = True, severity: str = "INFO"):
        event = {"timestamp": datetime.now().isoformat(), "event_type": event_type, "user_id": user_id, "action": action, "details": details or {}, "ip_address": ip_address, "success": success, "severity": severity}
        with self._lock:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")

    def log_login(self, user_id: str, ip: str, success: bool, reason: str = ""):
        self.log("LOGIN", user_id, "ورود", {"reason": reason} if reason else {}, ip, success, "WARNING" if not success else "INFO")

    def log_trade_open(self, user_id: str, symbol: str, volume: float, direction: str):
        self.log("TRADE_OPEN", user_id, f"باز کردن {symbol}", {"symbol": symbol, "volume": volume, "direction": direction})

    def log_trade_close(self, user_id: str, symbol: str, pnl: float, reason: str):
        self.log("TRADE_CLOSE", user_id, f"بستن {symbol}", {"symbol": symbol, "pnl": pnl, "reason": reason})

    def log_settings_change(self, user_id: str, setting: str, old_value: str, new_value: str):
        self.log("SETTINGS_CHANGE", user_id, f"تغییر {setting}", {"old": old_value, "new": new_value})

    def get_recent_events(self, limit: int = 100) -> list:
        events = []
        try:
            with open(self.log_file, encoding="utf-8") as f:
                for line in f.readlines()[-limit:]:
                    try:
                        events.append(json.loads(line))
                    except:
                        pass
        except FileNotFoundError:
            pass
        return events[::-1]


audit_logger = AuditLogger()
