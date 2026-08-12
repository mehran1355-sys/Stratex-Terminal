"""
رمزنگاری داده‌های حساس
"""

import base64
import hashlib
import secrets
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    def __init__(self, master_key: str = None):
        self.master_key = master_key or secrets.token_hex(32)
        key_bytes = hashlib.sha256(self.master_key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        self._fernet = Fernet(fernet_key)

    def encrypt(self, plaintext: str) -> str:
        encrypted = self._fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        encrypted = base64.urlsafe_b64decode(ciphertext.encode())
        return self._fernet.decrypt(encrypted).decode()

    def encrypt_dict(self, data: dict, sensitive_keys: list) -> dict:
        result = data.copy()
        for key in sensitive_keys:
            if key in result and result[key]:
                result[key] = self.encrypt(str(result[key]))
        return result

    def decrypt_dict(self, data: dict, sensitive_keys: list) -> dict:
        result = data.copy()
        for key in sensitive_keys:
            if key in result and result[key]:
                try:
                    result[key] = self.decrypt(str(result[key]))
                except:
                    pass
        return result

    def generate_secure_token(self, length: int = 64) -> str:
        return secrets.token_hex(length)


encryption_manager = EncryptionManager()
