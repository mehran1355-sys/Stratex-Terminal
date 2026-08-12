"""
رجیستری سرورها - مدیریت دو لپ‌تاپ
Server Registry Module
"""

import hashlib
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ServerInfo:
    server_id: str
    name: str
    host: str
    port: int
    location: str
    status: str = "online"
    last_heartbeat: float = field(default_factory=time.time)
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    load: float = 0.0
    active_connections: int = 0


class ServerRegistry:
    def __init__(self, heartbeat_timeout: int = 30):
        self.servers: Dict[str, ServerInfo] = {}
        self.heartbeat_timeout = heartbeat_timeout
        self._active_server_id: Optional[str] = None

    def register(self, name: str, host: str, port: int, location: str = "unknown") -> str:
        unique = f"{name}:{host}:{port}:{location}:{time.time()}"
        server_id = hashlib.md5(unique.encode()).hexdigest()[:12]
        self.servers[server_id] = ServerInfo(server_id=server_id, name=name, host=host, port=port, location=location)
        if self._active_server_id is None:
            self._active_server_id = server_id
        logger.info(f"Server registered: {name} ({location}) - {server_id}")
        return server_id

    def heartbeat(self, server_id: str) -> bool:
        if server_id in self.servers:
            self.servers[server_id].last_heartbeat = time.time()
            self.servers[server_id].status = "online"
            return True
        return False

    def check_health(self):
        current = time.time()
        for sid, srv in self.servers.items():
            if current - srv.last_heartbeat > self.heartbeat_timeout:
                srv.status = "offline"
                if self._active_server_id == sid:
                    self._active_server_id = self._select_best_server()

    def get_active_server(self) -> Optional[ServerInfo]:
        self.check_health()
        if self._active_server_id and self._active_server_id in self.servers:
            srv = self.servers[self._active_server_id]
            if srv.status == "online":
                return srv
        self._active_server_id = self._select_best_server()
        return self.servers.get(self._active_server_id)

    def _select_best_server(self) -> Optional[str]:
        online = [(sid, s) for sid, s in self.servers.items() if s.status == "online"]
        if not online:
            return None
        home = [(sid, s) for sid, s in online if s.location == "home"]
        work = [(sid, s) for sid, s in online if s.location == "work"]
        priority = home + work
        if priority:
            best = min(priority, key=lambda x: x[1].load)
            return best[0]
        return online[0][0] if online else None

    def get_all_servers(self) -> List[Dict]:
        self.check_health()
        return [{"server_id": s.server_id, "name": s.name, "location": s.location, "status": s.status, "load": s.load, "is_active": s.server_id == self._active_server_id} for s in self.servers.values()]

    def get_server_count(self) -> Dict:
        online = sum(1 for s in self.servers.values() if s.status == "online")
        offline = sum(1 for s in self.servers.values() if s.status == "offline")
        return {"total": len(self.servers), "online": online, "offline": offline}
