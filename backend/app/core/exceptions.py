"""
Custom exception classes for the application
"""
from typing import Any, Dict, Optional
from backend.app.core.constants import *
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

# ═══════════════════════════════════════════════════════════
# VALIDATION EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class ValidationException(VerifyNewsException):
    """Base class for validation errors"""
    pass


class InvalidURLException(ValidationException):
    """Raised when URL format is invalid"""
    
    def __init__(self, url: str):
        super().__init__(
            message=f"Invalid URL format: {url}",
            error_code=ErrorCode.VAL_INVALID_URL,
            details={"url": url},
        )


class InvalidEmailException(ValidationException):
    """Raised when email format is invalid"""
    
    def __init__(self, email: str):
        super().__init__(
            message=f"Invalid email format: {email}",
            error_code=ErrorCode.VAL_INVALID_EMAIL,
            details={"email": email},
        )


class WeakPasswordException(ValidationException):
    """Raised when password doesn't meet requirements"""
    
    def __init__(self, requirements: Dict[str, bool]):
        super().__init__(
            message="Password does not meet security requirements",
            error_code=ErrorCode.VAL_WEAK_PASSWORD,
            details={"requirements": requirements},
        )


class TextTooShortException(ValidationException):
    """Raised when text is too short for processing"""
    
    def __init__(self, current_length: int, min_length: int):
        super().__init__(
            message=f"Text too short. Minimum {min_length} characters required, got {current_length}",
            error_code=ErrorCode.VAL_TEXT_TOO_SHORT,
            details={"current_length": current_length, "min_length": min_length},
        )


class TextTooLongException(ValidationException):
    """Raised when text exceeds maximum length"""
    
    def __init__(self, current_length: int, max_length: int):
        super().__init__(
            message=f"Text too long. Maximum {max_length} characters allowed, got {current_length}",
            error_code=ErrorCode.VAL_TEXT_TOO_LONG,
            details={"current_length": current_length, "max_length": max_length},
        )


# ═══════════════════════════════════════════════════════════
# RATE LIMITING EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class RateLimitException(VerifyNewsException):
    """Base class for rate limit errors"""
    pass


class RateLimitExceededException(RateLimitException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str, retry_after: int):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}. Try again in {retry_after} seconds.",
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            details={
                "limit": limit,
                "window": window,
                "retry_after": retry_after,
            },
        )


class VerificationLimitExceededException(RateLimitException):
    """Raised when daily verification limit is exceeded"""
    
    def __init__(self, daily_limit: int):
        super().__init__(
            message=f"Daily verification limit exceeded ({daily_limit} verifications per day)",
            error_code=ErrorCode.RATE_VERIFICATION_LIMIT,
            details={"daily_limit": daily_limit},
        )


# ═══════════════════════════════════════════════════════════
# RESOURCE EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class ResourceException(VerifyNewsException):
    """Base class for resource-related errors"""
    pass


class ResourceNotFoundException(ResourceException):
    """Raised when requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            message=f"{resource_type} not found: {resource_id}",
            error_code=ErrorCode.RES_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": resource_id},
        )


class ResourceAlreadyExistsException(ResourceException):
    """Raised when trying to create duplicate resource"""
    
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            message=f"{resource_type} already exists: {identifier}",
            error_code=ErrorCode.RES_ALREADY_EXISTS,
            details={"resource_type": resource_type, "identifier": identifier},
        )


# ═══════════════════════════════════════════════════════════
# VERIFICATION EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class VerificationException(VerifyNewsException):
    """Base class for verification errors"""
    pass


class InsufficientDataException(VerificationException):
    """Raised when not enough data for verification"""
    
    def __init__(self, required_sources: int, found_sources: int):
        super().__init__(
            message=f"Insufficient data for verification. Required: {required_sources} sources, Found: {found_sources}",
            error_code=ErrorCode.VER_INSUFFICIENT_DATA,
            details={
                "required_sources": required_sources,
                "found_sources": found_sources,
            },
        )


class ScrapingFailedException(VerificationException):
    """Raised when article scraping fails"""
    
    def __init__(self, url: str, reason: str):
        super().__init__(
            message=f"Failed to scrape article: {reason}",
            error_code=ErrorCode.VER_SCRAPING_FAILED,
            details={"url": url, "reason": reason},
        )


class NLPProcessingException(VerificationException):
    """Raised when NLP processing fails"""
    
    def __init__(self, reason: str):
        super().__init__(
            message=f"NLP processing failed: {reason}",
            error_code=ErrorCode.VER_NLP_FAILED,
            details={"reason": reason},
        )


class VerificationTimeoutException(VerificationException):
    """Raised when verification takes too long"""
    
    def __init__(self, timeout_seconds: int):
        super().__init__(
            message=f"Verification timed out after {timeout_seconds} seconds",
            error_code=ErrorCode.VER_TIMEOUT,
            details={"timeout_seconds": timeout_seconds},
        )


class NoSimilarArticlesException(VerificationException):
    """Raised when no similar articles are found"""
    
    def __init__(self):
        super().__init__(
            message="No similar articles found in database",
            error_code=ErrorCode.VER_NO_SIMILAR_ARTICLES,
        )


# ═══════════════════════════════════════════════════════════
# SCRAPING EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class ScrapingException(VerifyNewsException):
    """Base class for scraping errors"""
    pass


class ScrapingBlockedException(ScrapingException):
    """Raised when scraper is blocked by target site"""
    
    def __init__(self, url: str):
        super().__init__(
            message=f"Scraping blocked by target site: {url}",
            error_code=ErrorCode.SCR_BLOCKED,
            details={"url": url},
        )


class ScrapingTimeoutException(ScrapingException):
    """Raised when scraping request times out"""
    
    def __init__(self, url: str, timeout: int):
        super().__init__(
            message=f"Scraping timeout after {timeout} seconds: {url}",
            error_code=ErrorCode.SCR_TIMEOUT,
            details={"url": url, "timeout": timeout},
        )


class InvalidHTMLException(ScrapingException):
    """Raised when HTML parsing fails"""
    
    def __init__(self, url: str, reason: str):
        super().__init__(
            message=f"Invalid HTML content: {reason}",
            error_code=ErrorCode.SCR_PARSING_FAILED,
            details={"url": url, "reason": reason},
        )


class ScraperRateLimitedException(ScrapingException):
    """Raised when scraper hits rate limit"""
    
    def __init__(self, url: str, retry_after: int):
        super().__init__(
            message=f"Scraper rate limited. Retry after {retry_after} seconds",
            error_code=ErrorCode.SCR_RATE_LIMITED,
            details={"url": url, "retry_after": retry_after},
        )


# ═══════════════════════════════════════════════════════════
# DATABASE EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class DatabaseException(VerifyNewsException):
    """Base class for database errors"""
    pass


class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails"""
    
    def __init__(self, details: str):
        super().__init__(
            message="Database connection failed",
            error_code=ErrorCode.DB_CONNECTION_ERROR,
            details={"error": details},
        )


class QueryTimeoutException(DatabaseException):
    """Raised when database query times out"""
    
    def __init__(self, query: str, timeout: int):
        super().__init__(
            message=f"Query timed out after {timeout} seconds",
            error_code=ErrorCode.DB_QUERY_TIMEOUT,
            details={"query": query[:100], "timeout": timeout},
        )


# ═══════════════════════════════════════════════════════════
# SERVICE EXCEPTIONS
# ═══════════════════════════════════════════════════════════

class ServiceException(VerifyNewsException):
    """Base class for service-level errors"""
    pass


class InternalServerException(ServiceException):
    """Raised for unexpected internal errors"""
    
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            message="Internal server error",
            error_code=ErrorCode.SRV_INTERNAL_ERROR,
            details={"error": details} if details else {},
        )


class ServiceUnavailableException(ServiceException):
    """Raised when service is temporarily unavailable"""
    
    def __init__(self, service_name: str):
        super().__init__(
            message=f"Service temporarily unavailable: {service_name}",
            error_code=ErrorCode.SRV_SERVICE_UNAVAILABLE,
            details={"service": service_name},
        )


class ExternalAPIException(ServiceException):
    """Raised when external API call fails"""
    
    def __init__(self, api_name: str, status_code: int, details: str):
        super().__init__(
            message=f"External API error: {api_name}",
            error_code=ErrorCode.SRV_EXTERNAL_API_ERROR,
            details={
                "api": api_name,
                "status_code": status_code,
                "error": details,
            },
        )


# ═══════════════════════════════════════════════════════════
# EXCEPTION TO HTTP EXCEPTION MAPPER
# ═══════════════════════════════════════════════════════════

def map_exception_to_http(exc: VerifyNewsException) -> HTTPException:
    """
    Map custom exceptions to FastAPI HTTPException
    
    Args:
        exc: Custom exception instance
    
    Returns:
        HTTPException with appropriate status code and details
    """
    # Authentication exceptions -> 401
    if isinstance(exc, (InvalidCredentialsException, TokenExpiredException, InvalidTokenException)):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Permission exceptions -> 403
    if isinstance(exc, (InsufficientPermissionsException, AccountLockedException)):
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )
    
    # Validation exceptions -> 400 or 422
    if isinstance(exc, ValidationException):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )
    
    # Rate limit exceptions -> 429
    if isinstance(exc, RateLimitException):
        retry_after = exc.details.get("retry_after", 60)
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
            headers={"Retry-After": str(retry_after)},
        )
    
    # Resource not found -> 404
    if isinstance(exc, ResourceNotFoundException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )
    
    # Resource already exists -> 409
    if isinstance(exc, (ResourceAlreadyExistsException, EmailAlreadyExistsException)):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )
    
    # Service unavailable -> 503
    if isinstance(exc, ServiceUnavailableException):
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )
    
    # Verification/Scraping/NLP exceptions -> 422
    if isinstance(exc, (VerificationException, ScrapingException)):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details,
            },
        )
    
    # Default: Internal server error -> 500
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "message": exc.message or "Internal server error",
            "error_code": exc.error_code or ErrorCode.SRV_INTERNAL_ERROR,
            "details": exc.details,
        },
    )


# ═══════════════════════════════════════════════════════════
# GLOBAL EXCEPTION HANDLER (for use in main.py)
# ═══════════════════════════════════════════════════════════

from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


async def verifynews_exception_handler(request: Request, exc: VerifyNewsException) -> JSONResponse:
    """
    Global exception handler for custom exceptions
    
    Usage in main.py:
        app.add_exception_handler(VerifyNewsException, verifynews_exception_handler)
    """
    # Log the exception
    logger.error(
        f"Exception occurred: {exc.__class__.__name__}",
        extra={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )
    
    # Map to HTTP exception
    http_exc = map_exception_to_http(exc)
    
    return JSONResponse(
        status_code=http_exc.status_code,
        content=http_exc.detail,
        headers=http_exc.headers,
    )


# ═══════════════════════════════════════════════════════════
# UTILITY FUNCTIONS FOR EXCEPTION HANDLING
# ═══════════════════════════════════════════════════════════


def validate_email(email: str) -> None:
    """
    Validate email format
    
    Args:
        email: Email string to validate
    
    Raises:
        InvalidEmailException: If email is invalid
    """
    if not EMAIL_PATTERN.match(email):
        raise InvalidEmailException(email)


def validate_password(password: str) -> None:
    """
    Validate password strength
    
    Args:
        password: Password string to validate
    
    Raises:
        WeakPasswordException: If password doesn't meet requirements
    """
    requirements = {
        "min_length": len(password) >= PASSWORD_MIN_LENGTH,
        "max_length": len(password) <= PASSWORD_MAX_LENGTH,
        "has_uppercase": any(c.isupper() for c in password) if PASSWORD_REQUIRE_UPPERCASE else True,
        "has_lowercase": any(c.islower() for c in password) if PASSWORD_REQUIRE_LOWERCASE else True,
        "has_digit": any(c.isdigit() for c in password) if PASSWORD_REQUIRE_DIGIT else True,
        "has_special": any(not c.isalnum() for c in password) if PASSWORD_REQUIRE_SPECIAL else True,
    }
    
    if not all(requirements.values()):
        raise WeakPasswordException(requirements)


def validate_text_length(text: str, min_length: int = MIN_TEXT_LENGTH, max_length: int = MAX_TEXT_LENGTH) -> None:
    """
    Validate text length
    
    Args:
        text: Text string to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length
    
    Raises:
        TextTooShortException: If text is too short
        TextTooLongException: If text is too long
    """
    text_length = len(text)
    
    if text_length < min_length:
        raise TextTooShortException(text_length, min_length)
    
    if text_length > max_length:
        raise TextTooLongException(text_length, max_length)


def check_rate_limit(
    key: str,
    limit: int,
    window: int,
    redis_client,
) -> None:
    """
    Check if rate limit is exceeded
    
    Args:
        key: Redis key for rate limiting
        limit: Maximum number of requests
        window: Time window in seconds
        redis_client: Redis client instance
    
    Raises:
        RateLimitExceededException: If rate limit exceeded
    """
    current = redis_client.get(key)
    
    if current is None:
        # First request in window
        redis_client.setex(key, window, 1)
        return
    
    current_count = int(current)
    
    if current_count >= limit:
        ttl = redis_client.ttl(key)
        raise RateLimitExceededException(
            limit=limit,
            window=f"{window}s",
            retry_after=ttl if ttl > 0 else window,
        )
    
    # Increment counter
    redis_client.incr(key)