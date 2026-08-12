"""
مدیریت اطلاعات حساس
"""

import os
import json
from pathlib import Path
from typing import Optional
import logging
from .encryption import encryption_manager

logger = logging.getLogger(__name__)


class SecretsManager:
    def __init__(self, secrets_file: str = None):
        self.secrets_file = secrets_file or os.environ.get("SECRETS_FILE", "data/secrets.enc")
        self._secrets: dict = {}
        self._load()

    def _load(self):
        if not Path(self.secrets_file).exists():
            return
        try:
            with open(self.secrets_file) as f:
                decrypted = encryption_manager.decrypt(f.read())
                self._secrets = json.loads(decrypted)
        except Exception as e:
            logger.error(f"Error loading secrets: {e}")

    def save(self):
        json_data = json.dumps(self._secrets)
        encrypted = encryption_manager.encrypt(json_data)
        with open(self.secrets_file, "w") as f:
            f.write(encrypted)
        os.chmod(self.secrets_file, 0o600)

    def get(self, key: str, default: str = None) -> Optional[str]:
        return os.environ.get(key) or self._secrets.get(key, default)

    def set(self, key: str, value: str):
        self._secrets[key] = value
        self.save()

    @property
    def telegram_token(self) -> Optional[str]:
        return self.get("TELEGRAM_BOT_TOKEN")


secrets_manager = SecretsManager()
