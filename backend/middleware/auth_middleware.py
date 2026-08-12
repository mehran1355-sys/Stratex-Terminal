"""
میدلور احراز هویت
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from security.auth import auth_manager, User, UserRole

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    payload = auth_manager.verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="توکن نامعتبر")
    user = auth_manager.users.get(payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="دسترسی غیرمجاز")
    return user


def require_role(role: UserRole):
    async def checker(user: User = Depends(get_current_user)):
        if role == UserRole.SUPER_ADMIN and user.role != UserRole.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="نیاز به دسترسی ادمین")
        if role == UserRole.ADMIN and user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            raise HTTPException(status_code=403, detail="نیاز به دسترسی ادمین")
        if role == UserRole.TRADER and user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.TRADER]:
            raise HTTPException(status_code=403, detail="نیاز به دسترسی معامله‌گر")
        return user
    return checker


require_admin = require_role(UserRole.ADMIN)
require_trader = require_role(UserRole.TRADER)
