"""
Custom exception classes for the application
"""
from typing import Any, Dict, Optional
from backend.app.core.constants import ErrorCode
from fastapi import HTTPException, status


# ═══════════════════════════════════════════════════════════
# BASE EXCEPTION
# ═══════════════════════════════════════════════════════════

class VerifyNewsException(Exception):
    """Base exception for all custom exceptions"""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# ═══════════════════════════════════════════════════════════
# AUTHENTICATION & AUTHORIZATION EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class AuthenticationException(VerifyNewsException):
    """Base class for authentication errors"""
    pass


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""
    
    def __init__(self):
        super().__init__(
            message="Invalid email or password",
            error_code=ErrorCode.AUTH_INVALID_CREDENTIALS,
        )


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""
    
    def __init__(self):
        super().__init__(
            message="Token has expired",
            error_code=ErrorCode.AUTH_TOKEN_EXPIRED,
        )


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid"""
    
    def __init__(self):
        super().__init__(
            message="Invalid authentication token",
            error_code=ErrorCode.AUTH_INVALID_TOKEN,
        )


class InsufficientPermissionsException(AuthenticationException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, required_role: str = "admin"):
        super().__init__(
            message=f"Insufficient permissions. Required role: {required_role}",
            error_code=ErrorCode.AUTH_INSUFFICIENT_PERMISSIONS,
            details={"required_role": required_role},
        )


class AccountLockedException(AuthenticationException):
    """Raised when account is locked due to too many failed attempts"""
    
    def __init__(self, lockout_minutes: int = 15):
        super().__init__(
            message=f"Account locked due to too many failed login attempts. Try again in {lockout_minutes} minutes.",
            error_code=ErrorCode.AUTH_ACCOUNT_LOCKED,
            details={"lockout_minutes": lockout_minutes},
        )


class EmailAlreadyExistsException(AuthenticationException):
    """Raised when trying to register with existing email"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"Email already registered: {email}",
            error_code=ErrorCode.AUTH_EMAIL_ALREADY_EXISTS,
            details={"email": email},
        )