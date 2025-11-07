"""News verification domain service based on documentation guidelines."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Iterable, List, Optional, Sequence, Tuple

from backend.app.core.constants import (
    ConfidenceLevel,
    DIVERSITY_THRESHOLD,
    MIN_SOURCES_DISPUTED,
    MIN_SOURCES_FOR_VERIFICATION,
    MIN_SOURCES_LIKELY_TRUE,
    MIN_SOURCES_UNCERTAIN,
    MIN_SOURCES_VERIFIED,
    SCORE_DISPUTED,
    SCORE_LIKELY_TRUE,
    SCORE_UNCERTAIN,
    SCORE_VERIFIED,
    SIMILARITY_THRESHOLD,
    VerificationStatus,
)
from backend.app.core.exceptions import (
    InsufficientDataException,
    NoSimilarArticlesException,
)


@dataclass(frozen=True)
class SimilarArticle:
    """Normalized representation of a similar article returned from search."""

    source_id: str
    similarity: float
    credibility: float
    source_name: Optional[str] = None
    published_at: Optional[datetime] = None
    country_code: Optional[str] = None
    url: Optional[str] = None

    def normalized_similarity(self) -> float:
        """Return similarity clipped to the 0-1 range."""

        return _clamp(self.similarity, 0.0, 1.0)

    def normalized_credibility(self) -> float:
        """Return credibility clipped to the 0-1 range."""

        return _clamp(self.credibility, 0.0, 1.0)


@dataclass(frozen=True)
class VerificationResult:
    """Domain response describing the verification decision."""

    score: float
    status: VerificationStatus
    confidence: ConfidenceLevel
    unique_sources: int
    diversity_factor: float
    recency_factor: float
    geography_factor: float
    reasoning: str
    supporting_articles: Sequence[SimilarArticle]


class VerificationService:
    """Service responsible for calculating verification scores and statuses."""

    def __init__(
        self,
        *,
        similarity_threshold: float = SIMILARITY_THRESHOLD,
        min_sources: int = MIN_SOURCES_FOR_VERIFICATION,
        diversity_threshold: int = DIVERSITY_THRESHOLD,
    ) -> None:
        self._similarity_threshold = similarity_threshold
        self._min_sources = min_sources
        self._diversity_threshold = diversity_threshold
        self._status_requirements: List[Tuple[VerificationStatus, float, int]] = [
            (VerificationStatus.VERIFIED, SCORE_VERIFIED, MIN_SOURCES_VERIFIED),
            (VerificationStatus.LIKELY_TRUE, SCORE_LIKELY_TRUE, MIN_SOURCES_LIKELY_TRUE),
            (VerificationStatus.UNCERTAIN, SCORE_UNCERTAIN, MIN_SOURCES_UNCERTAIN),
            (VerificationStatus.DISPUTED, SCORE_DISPUTED, MIN_SOURCES_DISPUTED),
        ]

    def verify(self, articles: Iterable[SimilarArticle]) -> VerificationResult:
        """Run the verification algorithm using the official specification."""

        selected = self._select_articles(articles)
        if not selected:
            raise NoSimilarArticlesException()

        unique_sources = {item.source_id for item in selected}
        if len(unique_sources) < self._min_sources:
            raise InsufficientDataException(self._min_sources, len(unique_sources))

        weighted_average = self._calculate_weighted_average(selected)
        diversity_factor = self._calculate_diversity_factor(len(unique_sources))
        recency_factor = self._calculate_recency_factor(selected)
        geography_factor = self._calculate_geography_factor(selected)

        raw_score = weighted_average * diversity_factor * recency_factor * geography_factor
        score = _clamp(round(raw_score, 4), 0.0, 1.0)

        status, reasoning = self._determine_status(score, len(unique_sources))
        confidence = self._determine_confidence(score)

        return VerificationResult(
            score=score,
            status=status,
            confidence=confidence,
            unique_sources=len(unique_sources),
            diversity_factor=diversity_factor,
            recency_factor=recency_factor,
            geography_factor=geography_factor,
            reasoning=reasoning,
            supporting_articles=selected,
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Core calculation steps
    # ──────────────────────────────────────────────────────────────────────────

    def _select_articles(self, articles: Iterable[SimilarArticle]) -> List[SimilarArticle]:
        """Filter and normalize candidate articles based on similarity threshold."""

        return [
            SimilarArticle(
                source_id=item.source_id,
                similarity=item.normalized_similarity(),
                credibility=item.normalized_credibility(),
                source_name=item.source_name,
                published_at=item.published_at,
                country_code=item.country_code,
                url=item.url,
            )
            for item in articles
            if item.normalized_similarity() >= self._similarity_threshold
        ]

    @staticmethod
    def _calculate_weighted_average(articles: Sequence[SimilarArticle]) -> float:
        """Compute Σ credibility × similarity / n."""

        if not articles:
            return 0.0
        weighted_sum = sum(item.credibility * item.similarity for item in articles)
        return weighted_sum / len(articles)

    def _calculate_diversity_factor(self, unique_sources: int) -> float:
        """Apply diversity factor based on the number of independent sources."""

        if unique_sources <= 0:
            return 0.0
        return min(unique_sources / float(self._diversity_threshold), 1.0)

    @staticmethod
    def _calculate_recency_factor(articles: Sequence[SimilarArticle]) -> float:
        """Return recency multiplier as described in the documentation."""

        recency_weights: List[float] = []
        hourly_buckets = {}
        now = datetime.now(timezone.utc)

        for article in articles:
            published_at = article.published_at
            if not published_at:
                continue
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            age_days = (now - published_at).total_seconds() / 86400
            if age_days <= 7:
                recency_weights.append(1.0)
            elif age_days <= 30:
                recency_weights.append(0.8)
            elif age_days <= 90:
                recency_weights.append(0.5)
            else:
                recency_weights.append(0.2)

            hour_bucket = published_at.replace(minute=0, second=0, microsecond=0)
            hourly_buckets.setdefault(hour_bucket, 0)
            hourly_buckets[hour_bucket] += 1

        if not recency_weights:
            base_factor = 1.0
        else:
            base_factor = mean(recency_weights)

        # Apply boosting if multiple articles are reported in the same hour.
        same_hour_max = max(hourly_buckets.values()) if hourly_buckets else 0
        if same_hour_max >= 3:
            boost = min(1.0 + (same_hour_max / len(articles)) * 0.2, 1.2)
            return _clamp(base_factor * boost, 0.0, 1.2)
        return _clamp(base_factor, 0.0, 1.0)

    @staticmethod
    def _calculate_geography_factor(articles: Sequence[SimilarArticle]) -> float:
        """Return geographic diversity multiplier if country codes are provided."""

        countries = {
            article.country_code.upper()
            for article in articles
            if article.country_code
        }
        if not countries:
            return 1.0
        return min(len(countries) / 5.0, 1.0)

    # ──────────────────────────────────────────────────────────────────────────
    # Status and confidence helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _determine_status(self, score: float, unique_sources: int) -> Tuple[VerificationStatus, str]:
        """Match score and source count to the appropriate verification status."""

        for status, min_score, min_sources in self._status_requirements:
            if score >= min_score and unique_sources >= min_sources:
                return status, self._status_reason(status)
        return VerificationStatus.UNVERIFIED, self._status_reason(VerificationStatus.UNVERIFIED)

    @staticmethod
    def _status_reason(status: VerificationStatus) -> str:
        """Human readable reasoning aligned with documentation table."""

        if status is VerificationStatus.VERIFIED:
            return "Multiple independent, high-credibility sources confirm the story."
        if status is VerificationStatus.LIKELY_TRUE:
            return "Story is supported by several reputable sources but lacks maximum coverage."
        if status is VerificationStatus.UNCERTAIN:
            return "Conflicting or limited sources — more verification required."
        if status is VerificationStatus.DISPUTED:
            return "Reports exist but reliability is questionable or contradictory."
        return "Insufficient trustworthy sources to verify the story."

    @staticmethod
    def _determine_confidence(score: float) -> ConfidenceLevel:
        """Translate the score into a qualitative confidence indicator."""

        if score >= SCORE_VERIFIED:
            return ConfidenceLevel.HIGH
        if score >= SCORE_UNCERTAIN:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW


def _clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a float value to the provided range."""

    return max(minimum, min(maximum, value))
