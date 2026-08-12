"""
سیستم احراز هویت JWT
"""

import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


class UserRole(Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    TRADER = "trader"
    ANALYST = "analyst"
    VIEWER = "viewer"


@dataclass
class User:
    user_id: str
    username: str
    email: str
    role: UserRole
    password_hash: str
    api_key: str = ""
    is_active: bool = True
    is_2fa_enabled: bool = False
    two_factor_secret: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class AuthManager:
    def __init__(self, secret_key: str = None, token_expiry_minutes: int = 60, max_failed_attempts: int = 5):
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_expiry = token_expiry_minutes
        self.max_failed_attempts = max_failed_attempts
        self.users: Dict[str, User] = {}
        self.refresh_tokens: Dict[str, str] = {}
        self.blacklisted_tokens: set = set()
        self._create_default_admin()

    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.VIEWER) -> User:
        if username in [u.username for u in self.users.values()]:
            raise ValueError(f"نام کاربری {username} تکراری است")
        user_id = f"USR_{secrets.token_hex(8)}"
        password_hash = self._hash_password(password)
        user = User(user_id=user_id, username=username, email=email, role=role, password_hash=password_hash, api_key=f"SD_{secrets.token_hex(24)}")
        self.users[user_id] = user
        return user

    def authenticate(self, username: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        user = next((u for u in self.users.values() if u.username == username), None)
        if not user:
            return None, "نام کاربری یا رمز عبور اشتباه است"
        if user.locked_until and user.locked_until > datetime.now():
            return None, "حساب کاربری قفل است"
        if not user.is_active:
            return None, "حساب غیرفعال است"
        if not self._verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= self.max_failed_attempts:
                user.locked_until = datetime.now() + timedelta(minutes=30)
            return None, "نام کاربری یا رمز عبور اشتباه است"
        user.failed_login_attempts = 0
        user.last_login = datetime.now()
        return user, None

    def generate_tokens(self, user: User) -> TokenPair:
        access_payload = {"sub": user.user_id, "username": user.username, "role": user.role.value, "type": "access", "iat": datetime.utcnow(), "exp": datetime.utcnow() + timedelta(minutes=self.token_expiry)}
        refresh_payload = {"sub": user.user_id, "type": "refresh", "iat": datetime.utcnow(), "exp": datetime.utcnow() + timedelta(days=30)}
        access_token = jwt.encode(access_payload, self.secret_key, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm="HS256")
        self.refresh_tokens[hashlib.sha256(refresh_token.encode()).hexdigest()] = user.user_id
        return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=self.token_expiry * 60)

    def verify_token(self, token: str) -> Optional[Dict]:
        if token in self.blacklisted_tokens:
            return None
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            if payload.get("type") != "access" or payload.get("sub") not in self.users:
                return None
            return payload
        except jwt.InvalidTokenError:
            return None

    def logout(self, access_token: str, refresh_token: str = None):
        self.blacklisted_tokens.add(access_token)
        if refresh_token:
            self.refresh_tokens.pop(hashlib.sha256(refresh_token.encode()).hexdigest(), None)

    def _hash_password(self, password: str) -> str:
        import bcrypt
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        import bcrypt
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def _create_default_admin(self):
        try:
            self.create_user("admin", "admin@supplydemand.com", "Admin@123456!", UserRole.SUPER_ADMIN)
        except ValueError:
            pass


auth_manager = AuthManager()
