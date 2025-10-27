"""
Application-wide constants and enums
"""
from enum import Enum

# ═══════════════════════════════════════════════════════════
# DOĞRULAMA CONSTANTS
# ═══════════════════════════════════════════════════════════

class VerificationStatus(str, Enum):
    """doğrulama durumu kodları"""
    VERIFIED = "verified"
    LIKELY_TRUE = "likely_true"
    UNCERTAIN = "uncertain"
    DISPUTED = "disputed"
    UNVERIFIED = "unverified"
    PROCESSING = "processing"
    FAILED = "failed"


class ConfidenceLevel(str, Enum):
    """doğrulama güven seviyesi"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# puan eşikleri
SIMILARITY_THRESHOLD = 0.65  # haberleri benzer saymak için gerekli minimum benzerlik
DIVERSITY_THRESHOLD = 10  # çeşitlilik faktörü için gerekli kaynak sayısı
MIN_SOURCES_FOR_VERIFICATION = 3  # doğrulama denemesi için gerekli minimum kaynak

# puan karar verme için gerekli aralıklar
SCORE_VERIFIED = 0.80
SCORE_LIKELY_TRUE = 0.70
SCORE_UNCERTAIN = 0.50
SCORE_DISPUTED = 0.30

# kaynak sayı gereklilikleri (eg. "verified" için min. 10 kaynakta geçiyor olmalı)
MIN_SOURCES_VERIFIED = 10
MIN_SOURCES_LIKELY_TRUE = 7
MIN_SOURCES_UNCERTAIN = 5
MIN_SOURCES_DISPUTED = 3

# ═══════════════════════════════════════════════════════════
# KAYNAK GÜVENLİĞİ CONSTANTS
# ═══════════════════════════════════════════════════════════

class SourceBias(str, Enum):
    """News source bias rating"""
    LEFT = "left"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    RIGHT = "right"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    """Type of news source"""
    MAINSTREAM_MEDIA = "mainstream_media"
    INDEPENDENT_MEDIA = "independent_media"
    FACT_CHECKER = "fact_checker"
    GOVERNMENT = "government"
    BLOG = "blog"
    SOCIAL_MEDIA = "social_media"
    UNKNOWN = "unknown"


# kaynak güvenlik puanı aralıkları
CREDIBILITY_VERY_HIGH = 0.90  # BBC, Reuters vb. global kaynaklar
CREDIBILITY_HIGH = 0.80  # çok bilinen gazeteler
CREDIBILITY_MEDIUM = 0.65  # yerel haber, blog
CREDIBILITY_LOW = 0.40  # şüpheli kaynaklar

# ═══════════════════════════════════════════════════════════
# NLP & EMBEDDING CONSTANTS
# ═══════════════════════════════════════════════════════════

# model konfigürasyon
EMBEDDING_DIMENSION = 512  # vektör boyut (transformers)
SPACY_MODEL_NAME = "tr_core_news_lg"  # türkçe dil modeli
TRANSFORMERS_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# metin işleme
MAX_TEXT_LENGTH = 50000  # işlenebilir maksimum karakter
MIN_TEXT_LENGTH = 100  # işleme yapmak için gerekli minimum karakter

# benzerlik araması
MAX_SIMILAR_ARTICLES = 50  # çekilecek max. benzer haber sayısı
SIMILARITY_SEARCH_TIMEOUT = 5  # belirtilen sürede arama bitmezse timeout

# ═══════════════════════════════════════════════════════════
# RATE LIMITING CONSTANTS
# ═══════════════════════════════════════════════════════════

# Rate limits (requests per time window)
RATE_LIMIT_VERIFY_PER_MINUTE = 10  # dakikada max. doğrulama isteği
RATE_LIMIT_VERIFY_PER_HOUR = 50  # saatte max. doğrulama isteği
RATE_LIMIT_VERIFY_PER_DAY = 100  # günde max. doğrulama isteği

RATE_LIMIT_API_PER_MINUTE = 60  # dakikada max. genel api istekleri
RATE_LIMIT_API_PER_HOUR = 1000  # saatte max. genel api istekleri

RATE_LIMIT_AUTH_PER_MINUTE = 5  # dakikada max. giriş denemesi
RATE_LIMIT_AUTH_PER_HOUR = 20  # saat max. giriş denemesi

# Rate limit windows (seconds)
RATE_LIMIT_WINDOW_MINUTE = 60
RATE_LIMIT_WINDOW_HOUR = 3600
RATE_LIMIT_WINDOW_DAY = 86400

# ═══════════════════════════════════════════════════════════
# USER & AUTHENTICATION CONSTANTS
# ═══════════════════════════════════════════════════════════

# şifre gereklilikleri
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = False

# JWT token
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
ALGORITHM = "HS256"

# hesap kilitleme
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION = 900  # 15 dakika kilitli kalma süresi

# ═══════════════════════════════════════════════════════════
# TRENDLER & ANALİZ CONSTANTS
# ═══════════════════════════════════════════════════════════

# trend hesaplama
TRENDING_TOP_N = 50  # Top N keywords to store
TRENDING_MIN_KEYWORD_LENGTH = 3  # Minimum characters for keyword
TRENDING_MAX_KEYWORD_LENGTH = 50  # Maximum characters for keyword
TRENDING_MIN_OCCURRENCES = 3  # Minimum occurrences to be considered trending

# Time windows
TRENDING_WINDOW_DAILY = "daily"
TRENDING_WINDOW_WEEKLY = "weekly"
TRENDING_WINDOW_MONTHLY = "monthly"

# Recency boost
TRENDING_RECENCY_WINDOW_HOURS = 6  # Boost for articles in last N hours
TRENDING_RECENCY_BOOST_FACTOR = 1.5  # Multiplier for recent articles

# ═══════════════════════════════════════════════════════════
# DİLLER & YERELLEŞTİRME
# ═══════════════════════════════════════════════════════════

class SupportedLanguage(str, Enum):
    """Supported languages"""
    TURKISH = "tr"
    # farklı diller eklenebilir


DEFAULT_LANGUAGE = SupportedLanguage.TURKISH

# ═══════════════════════════════════════════════════════════
# HTTP STATUS CODES (commonly used)
# ═══════════════════════════════════════════════════════════

HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_503_SERVICE_UNAVAILABLE = 503


# ═══════════════════════════════════════════════════════════
# DATABASE CONSTANTS
# ═══════════════════════════════════════════════════════════

# Connection pool
DB_POOL_SIZE = 20
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30
DB_POOL_RECYCLE = 3600  # 1 hour

# Query timeouts
DB_QUERY_TIMEOUT = 10  # Seconds

# ═══════════════════════════════════════════════════════════
# CELERY TASK CONSTANTS
# ═══════════════════════════════════════════════════════════

class TaskPriority(int, Enum):
    """Celery task priority levels"""
    LOW = 3
    NORMAL = 5
    HIGH = 7
    CRITICAL = 9


# Task timeouts
TASK_TIMEOUT_VERIFICATION = 60  # Seconds
TASK_TIMEOUT_TREND_CALCULATION = 300  # Seconds

# Task retry
TASK_MAX_RETRIES = 3
TASK_RETRY_BACKOFF = True
TASK_RETRY_BACKOFF_MAX = 600  # 10 minutes

# ═══════════════════════════════════════════════════════════
# FILE & STORAGE CONSTANTS
# ═══════════════════════════════════════════════════════════

# Log retention
LOG_RETENTION_DAYS = 30
LOG_MAX_SIZE_MB = 100

# Data retention
DATA_RETENTION_DAYS_LOGS = 90
DATA_RETENTION_DAYS_VERIFICATIONS = 365
DATA_RETENTION_DAYS_SESSIONS = 30


# ═══════════════════════════════════════════════════════════
# REGEX PATTERNS
# ═══════════════════════════════════════════════════════════

import re

URL_PATTERN = re.compile(
    r'^https?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', 
    re.IGNORECASE
)

EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

# Turkish characters included
KEYWORD_PATTERN = re.compile(
    r'^[a-zA-ZçÇğĞıİöÖşŞüÜ\s-]{3,50}$'
)


# ═══════════════════════════════════════════════════════════
# ERROR CODES
# ═══════════════════════════════════════════════════════════

class ErrorCode(str, Enum):
    """UYGULAMA ÖZELİNDE HATA KODLARI"""
    # Authentication errors (AUTH_xxx)
    AUTH_INVALID_CREDENTIALS = "AUTH_001"
    AUTH_TOKEN_EXPIRED = "AUTH_002"
    AUTH_INVALID_TOKEN = "AUTH_003"
    AUTH_INSUFFICIENT_PERMISSIONS = "AUTH_004"
    AUTH_ACCOUNT_LOCKED = "AUTH_005"
    AUTH_EMAIL_ALREADY_EXISTS = "AUTH_006"
    
    # Validation errors (VAL_xxx)
    VAL_INVALID_URL = "VAL_001"
    VAL_INVALID_EMAIL = "VAL_002"
    VAL_WEAK_PASSWORD = "VAL_003"
    VAL_MISSING_FIELD = "VAL_004"
    VAL_TEXT_TOO_SHORT = "VAL_005"
    VAL_TEXT_TOO_LONG = "VAL_006"
    
    # Rate limit errors (RATE_xxx)
    RATE_LIMIT_EXCEEDED = "RATE_001"
    RATE_VERIFICATION_LIMIT = "RATE_002"
    RATE_API_LIMIT = "RATE_003"
    
    # Resource errors (RES_xxx)
    RES_NOT_FOUND = "RES_001"
    RES_ALREADY_EXISTS = "RES_002"
    RES_DELETED = "RES_003"
    
    # Verification errors (VER_xxx)
    VER_INSUFFICIENT_DATA = "VER_001"
    VER_SCRAPING_FAILED = "VER_002"
    VER_NLP_FAILED = "VER_003"
    VER_TIMEOUT = "VER_004"
    VER_NO_SIMILAR_ARTICLES = "VER_005"
    
    # Scraping errors (SCR_xxx)
    SCR_BLOCKED = "SCR_001"
    SCR_TIMEOUT = "SCR_002"
    SCR_INVALID_RESPONSE = "SCR_003"
    SCR_PARSING_FAILED = "SCR_004"
    SCR_RATE_LIMITED = "SCR_005"
    
    # Database errors (DB_xxx)
    DB_CONNECTION_ERROR = "DB_001"
    DB_QUERY_TIMEOUT = "DB_002"
    DB_CONSTRAINT_VIOLATION = "DB_003"
    
    # Service errors (SRV_xxx)
    SRV_INTERNAL_ERROR = "SRV_001"
    SRV_SERVICE_UNAVAILABLE = "SRV_002"
    SRV_EXTERNAL_API_ERROR = "SRV_003"


# ═══════════════════════════════════════════════════════════
# SUCCESS MESSAGES
# ═══════════════════════════════════════════════════════════

SUCCESS_USER_REGISTERED = "User registered successfully"
SUCCESS_USER_LOGGED_IN = "Login successful"
SUCCESS_VERIFICATION_COMPLETED = "Verification completed"
SUCCESS_ARTICLE_SCRAPED = "Article scraped successfully"
SUCCESS_SOURCE_ADDED = "News source added"
SUCCESS_DATA_UPDATED = "Data updated successfully"
SUCCESS_DATA_DELETED = "Data deleted successfully"

# ═══════════════════════════════════════════════════════════
# TURKISH STOP WORDS (for NLP processing)
# ═══════════════════════════════════════════════════════════

TURKISH_STOP_WORDS = {
    "ve", "veya", "ile", "için", "bir", "bu", "şu", "o", "da", "de",
    "mi", "mı", "mu", "mü", "ama", "fakat", "ancak", "lakin", "ne",
    "ki", "dahi", "gibi", "kadar", "çok", "az", "en", "daha", "pek",
    "hem", "ya", "yahut", "var", "yok", "her", "bazı", "birçok",
    "birkaç", "tüm", "bütün", "hangi", "hiç", "hiçbir", "kendi",
}