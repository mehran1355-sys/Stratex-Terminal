"""
محدودیت نرخ درخواست‌ها
Rate Limiter
"""

import time
import threading
from collections import defaultdict
from typing import Dict, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitRule:
    max_requests: int
    window_seconds: int
    block_duration_seconds: int = 300


class RateLimiter:
    def __init__(self):
        self.rules = {
            "default": RateLimitRule(60, 60),
            "analysis": RateLimitRule(10, 60),
            "trade": RateLimitRule(5, 60),
            "login": RateLimitRule(5, 900, 1800),
        }
        self._requests: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self._blocked: Dict[str, Dict[str, float]] = defaultdict(dict)
        self._lock = threading.Lock()

    def check(self, client_id: str, endpoint_type: str = "default") -> Tuple[bool, str]:
        rule = self.rules.get(endpoint_type, self.rules["default"])
        now = time.time()
        with self._lock:
            if client_id in self._blocked[endpoint_type]:
                if now < self._blocked[endpoint_type][client_id]:
                    remaining = int(self._blocked[endpoint_type][client_id] - now)
                    return False, f"محدودیت نرخ. {remaining} ثانیه صبر کنید"
                del self._blocked[endpoint_type][client_id]
            self._requests[endpoint_type][client_id] = [t for t in self._requests[endpoint_type][client_id] if now - t < rule.window_seconds]
            if len(self._requests[endpoint_type][client_id]) >= rule.max_requests:
                self._blocked[endpoint_type][client_id] = now + rule.block_duration_seconds
                return False, f"تعداد درخواست‌ها بیش از حد مجاز"
            self._requests[endpoint_type][client_id].append(now)
            remaining = rule.max_requests - len(self._requests[endpoint_type][client_id])
            return True, f"مجاز ({remaining} باقی‌مانده)"

    def reset(self, client_id: str, endpoint_type: str = None):
        with self._lock:
            if endpoint_type:
                self._requests[endpoint_type].pop(client_id, None)
                self._blocked[endpoint_type].pop(client_id, None)
            else:
                for ep in self._requests:
                    self._requests[ep].pop(client_id, None)
                    self._blocked[ep].pop(client_id, None)


rate_limiter = RateLimiter()
