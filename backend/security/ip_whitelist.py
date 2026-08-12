"""
لیست سفید و سیاه IP
"""

import ipaddress
from typing import Set
import logging

logger = logging.getLogger(__name__)


class IPWhitelist:
    def __init__(self):
        self.whitelist: Set[str] = set()
        self.blacklist: Set[str] = set()
        self.enable_whitelist: bool = False
        self.enable_blacklist: bool = True
        self.auto_block_threshold: int = 10
        self.failed_attempts: dict = {}

    def is_allowed(self, ip: str) -> bool:
        if self.enable_blacklist and self._is_ip_in_list(ip, self.blacklist):
            return False
        if self.enable_whitelist:
            return self._is_ip_in_list(ip, self.whitelist)
        return True

    def add_to_whitelist(self, ip: str):
        self.whitelist.add(ip)

    def add_to_blacklist(self, ip: str, reason: str = ""):
        self.blacklist.add(ip)
        logger.warning(f"IP blacklisted: {ip} ({reason})")

    def record_failed_attempt(self, ip: str):
        self.failed_attempts[ip] = self.failed_attempts.get(ip, 0) + 1
        if self.failed_attempts[ip] >= self.auto_block_threshold:
            self.add_to_blacklist(ip, "تلاش ناموفق متعدد")

    def _is_ip_in_list(self, ip: str, ip_list: Set[str]) -> bool:
        try:
            client_ip = ipaddress.ip_address(ip)
            for entry in ip_list:
                try:
                    if client_ip in ipaddress.ip_network(entry, strict=False):
                        return True
                except:
                    continue
            return False
        except ValueError:
            return False

    def get_stats(self) -> dict:
        return {"whitelist_count": len(self.whitelist), "blacklist_count": len(self.blacklist)}


ip_whitelist = IPWhitelist()
