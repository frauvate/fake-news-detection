"""Utilities for assigning trust scores to news sources."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Optional

from backend.app.core.constants import (
    CREDIBILITY_HIGH,
    CREDIBILITY_LOW,
    CREDIBILITY_MEDIUM,
    CREDIBILITY_VERY_HIGH,
    SourceBias,
    SourceType,
)
from backend.app.core.exceptions import VerificationException


@dataclass(frozen=True)
class SourceTrustMetrics:
    """Behavioral metrics describing a news source."""

    accuracy_history: float
    editorial_standards: float
    transparency_level: float
    correction_speed: float

    def normalized(self) -> "SourceTrustMetrics":
        return SourceTrustMetrics(
            accuracy_history=_clamp(self.accuracy_history, 0.0, 1.0),
            editorial_standards=_clamp(self.editorial_standards, 0.0, 1.0),
            transparency_level=_clamp(self.transparency_level, 0.0, 1.0),
            correction_speed=_clamp(self.correction_speed, 0.0, 1.0),
        )


@dataclass(frozen=True)
class SourceTrustScore:
    """Outcome of a trust score calculation."""

    score: float
    tier: str
    method: str
    rationale: str
    components: Mapping[str, float]


class SourceTrustService:
    """Service that encapsulates the trust score logic for news sources."""

    def __init__(
        self,
        *,
        manual_overrides: Optional[Mapping[str, float]] = None,
        bias_adjustments: Optional[Mapping[SourceBias, float]] = None,
    ) -> None:
        self._overrides: Dict[str, float] = dict(manual_overrides or {})
        self._bias_adjustments: Dict[SourceBias, float] = dict(bias_adjustments or {})
        self._baseline_by_type: Mapping[SourceType, float] = {
            SourceType.FACT_CHECKER: CREDIBILITY_VERY_HIGH,
            SourceType.MAINSTREAM_MEDIA: CREDIBILITY_HIGH,
            SourceType.GOVERNMENT: CREDIBILITY_HIGH,
            SourceType.INDEPENDENT_MEDIA: CREDIBILITY_MEDIUM,
            SourceType.BLOG: CREDIBILITY_LOW,
            SourceType.SOCIAL_MEDIA: CREDIBILITY_LOW,
            SourceType.UNKNOWN: CREDIBILITY_LOW,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Manual configuration methods
    # ──────────────────────────────────────────────────────────────────────────

    def register_manual_override(self, source_id: str, score: float) -> None:
        """Persist a manual score override for a specific source."""

        self._overrides[source_id] = _clamp(score, 0.0, 1.0)

    def calculate_manual_score(
        self,
        *,
        source_id: str,
        source_type: SourceType,
        bias: SourceBias = SourceBias.UNKNOWN,
    ) -> SourceTrustScore:
        """Return the manual MVP style trust score recommended in the documentation."""

        base_score = self._overrides.get(source_id)
        if base_score is None:
            base_score = self._baseline_by_type.get(source_type, CREDIBILITY_LOW)
        adjusted = self._apply_bias_adjustment(base_score, bias)
        rationale = (
            "Manual baseline derived from source type and optional editorial overrides."
        )
        return SourceTrustScore(
            score=adjusted,
            tier=self._classify(adjusted),
            method="manual",
            rationale=rationale,
            components={"base_score": base_score, "bias_adjustment": adjusted - base_score},
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Dynamic scoring based on behavioral metrics
    # ──────────────────────────────────────────────────────────────────────────

    def calculate_dynamic_score(
        self,
        metrics: SourceTrustMetrics,
        *,
        source_type: SourceType = SourceType.UNKNOWN,
        bias: SourceBias = SourceBias.UNKNOWN,
        blend_with_manual: bool = True,
    ) -> SourceTrustScore:
        """Compute a trust score using weighted behavioral metrics."""

        normalized = metrics.normalized()
        dynamic_score = (
            normalized.accuracy_history * 0.40
            + normalized.editorial_standards * 0.30
            + normalized.transparency_level * 0.20
            + normalized.correction_speed * 0.10
        )

        if blend_with_manual:
            baseline = self._baseline_by_type.get(source_type, CREDIBILITY_LOW)
            dynamic_score = (dynamic_score + baseline) / 2.0

        adjusted = self._apply_bias_adjustment(dynamic_score, bias)
        rationale = (
            "Weighted metrics (accuracy, editorial standards, transparency, correction speed)"
            " blended with type baseline" if blend_with_manual else "Weighted behavioral metrics"
        )
        return SourceTrustScore(
            score=adjusted,
            tier=self._classify(adjusted),
            method="dynamic",
            rationale=rationale,
            components={
                "accuracy_history": normalized.accuracy_history,
                "editorial_standards": normalized.editorial_standards,
                "transparency_level": normalized.transparency_level,
                "correction_speed": normalized.correction_speed,
                "baseline": self._baseline_by_type.get(source_type, CREDIBILITY_LOW)
                if blend_with_manual
                else 0.0,
                "bias_adjustment": adjusted - dynamic_score,
            },
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Aggregation helpers
    # ──────────────────────────────────────────────────────────────────────────

    def combine_scores(
        self,
        manual_score: SourceTrustScore,
        dynamic_score: SourceTrustScore,
        *,
        manual_weight: float = 0.5,
    ) -> SourceTrustScore:
        """Combine manual and dynamic scores into a single trust rating."""

        manual_weight = _clamp(manual_weight, 0.0, 1.0)
        combined_value = manual_score.score * manual_weight + dynamic_score.score * (
            1.0 - manual_weight
        )
        rationale = (
            "Blended manual and dynamic trust scores with weights"
            f" manual={manual_weight:.2f}, dynamic={(1.0 - manual_weight):.2f}."
        )
        return SourceTrustScore(
            score=_clamp(combined_value, 0.0, 1.0),
            tier=self._classify(combined_value),
            method="hybrid",
            rationale=rationale,
            components={
                "manual_score": manual_score.score,
                "dynamic_score": dynamic_score.score,
                "manual_weight": manual_weight,
            },
        )

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _apply_bias_adjustment(self, score: float, bias: SourceBias) -> float:
        adjustment = self._bias_adjustments.get(bias, 0.0)
        return _clamp(score + adjustment, 0.0, 1.0)

    @staticmethod
    def _classify(score: float) -> str:
        if score >= CREDIBILITY_VERY_HIGH:
            return "very_high"
        if score >= CREDIBILITY_HIGH:
            return "high"
        if score >= CREDIBILITY_MEDIUM:
            return "medium"
        if score > CREDIBILITY_LOW:
            return "low"
        return "very_low"


def _clamp(value: float, minimum: float, maximum: float) -> float:
    if minimum > maximum:
        raise VerificationException("Invalid clamp range")
    return max(minimum, min(maximum, value))
