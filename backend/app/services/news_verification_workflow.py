"""Application service orchestrating search and verification pipeline."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Mapping, MutableMapping, Optional, Sequence, Tuple

from backend.app.core.constants import (
    MAX_SIMILAR_ARTICLES,
    SourceBias,
    SourceType,
    VerificationStatus,
)
from backend.app.core.mongo import search_news_atlas, search_news_regex
from backend.app.services.source_trust_service import SourceTrustService
from backend.app.services.verification_service import (
    SimilarArticle,
    VerificationResult,
    VerificationService,
)
from backend.app.utils.text_processing import prepare_for_similarity_search


@dataclass(frozen=True)
class VerificationWorkflowResult:
    """DTO returned by the verification workflow."""

    clean_text: str
    verification: VerificationResult
    articles: Sequence[Dict[str, object]]
    fallback_used: bool


class NewsVerificationWorkflow:
    """High level coordinator for search → verification flow."""

    def __init__(
        self,
        *,
        verification_service: Optional[VerificationService] = None,
        trust_service: Optional[SourceTrustService] = None,
        source_type_overrides: Optional[Mapping[str, SourceType]] = None,
        source_bias_overrides: Optional[Mapping[str, SourceBias]] = None,
        default_limit: int = MAX_SIMILAR_ARTICLES,
    ) -> None:
        self._verification_service = verification_service or VerificationService()
        self._trust_service = trust_service or SourceTrustService()
        self._source_type_overrides: Dict[str, SourceType] = dict(source_type_overrides or {})
        self._source_bias_overrides: Dict[str, SourceBias] = dict(source_bias_overrides or {})
        self._default_limit = min(default_limit, MAX_SIMILAR_ARTICLES)

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────

    def verify_text(self, text: str, *, limit: Optional[int] = None) -> VerificationWorkflowResult:
        """Run the search pipeline and verification algorithm for the text."""

        clean_text = prepare_for_similarity_search(text)
        documents, fallback_used = self._search_similar_articles(clean_text, limit)
        articles, lookup = self._transform_documents(documents)
        verification = self._verification_service.verify(articles)
        enriched = self._merge_metadata(verification.supporting_articles, lookup)

        return VerificationWorkflowResult(
            clean_text=clean_text,
            verification=verification,
            articles=enriched,
            fallback_used=fallback_used,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────

    def _search_similar_articles(
        self, clean_text: str, limit: Optional[int]
    ) -> Tuple[Sequence[Dict[str, object]], bool]:
        search_limit = self._determine_limit(limit)
        try:
            documents = search_news_atlas(clean_text, limit=search_limit)
            return documents, False
        except Exception:
            documents = search_news_regex(clean_text, limit=search_limit)
            return documents, True

    def _determine_limit(self, limit: Optional[int]) -> int:
        if limit is None:
            return self._default_limit
        if limit <= 0:
            return 1
        return min(limit, MAX_SIMILAR_ARTICLES)

    def _transform_documents(
        self, documents: Sequence[Mapping[str, object]]
    ) -> Tuple[List[SimilarArticle], MutableMapping[Tuple[str, Optional[str]], Mapping[str, object]]]:
        articles: List[SimilarArticle] = []
        lookup: Dict[Tuple[str, Optional[str]], Mapping[str, object]] = {}
        for doc in documents:
            article = self._build_similar_article(doc)
            articles.append(article)
            lookup[self._article_key(article)] = doc
        return articles, lookup

    def _build_similar_article(self, document: Mapping[str, object]) -> SimilarArticle:
        source_id = self._extract_source_id(document)
        similarity = self._extract_similarity(document)
        credibility = self._extract_credibility(document, source_id)
        published_at = self._parse_datetime(document.get("tarih"))
        source_name = self._coerce_str(document.get("kaynak"))
        country_code = self._coerce_country(document.get("ulke"))
        url = self._coerce_str(document.get("url"))

        return SimilarArticle(
            source_id=source_id,
            similarity=similarity,
            credibility=credibility,
            source_name=source_name,
            published_at=published_at,
            country_code=country_code,
            url=url,
        )

    def _extract_source_id(self, document: Mapping[str, object]) -> str:
        for key in ("kaynak_id", "kaynak", "source_id", "_id", "url"):
            value = document.get(key)
            if value:
                return str(value)
        fallback = document.get("baslik") or document.get("ozet")
        if fallback:
            return str(fallback)
        return f"anonymous-{id(document)}"

    def _extract_similarity(self, document: Mapping[str, object]) -> float:
        raw = document.get("score")
        try:
            value = float(raw) if raw is not None else 0.0
        except (TypeError, ValueError):
            value = 0.0
        if value > 1.0:
            return 1.0
        return max(0.0, value)

    def _extract_credibility(self, document: Mapping[str, object], source_id: str) -> float:
        for key in ("credibility", "trust_score", "guvenilirlik"):
            raw = document.get(key)
            if raw is not None:
                try:
                    return max(0.0, min(float(raw), 1.0))
                except (TypeError, ValueError):
                    continue
        source_type = self._source_type_overrides.get(source_id, SourceType.UNKNOWN)
        bias = self._source_bias_overrides.get(source_id, SourceBias.UNKNOWN)
        trust = self._trust_service.calculate_manual_score(
            source_id=source_id,
            source_type=source_type,
            bias=bias,
        )
        return trust.score

    def _parse_datetime(self, value: object) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and value:
            for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    parsed = datetime.strptime(value, fmt)
                    return parsed
                except ValueError:
                    continue
        return None

    def _coerce_str(self, value: object) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    def _coerce_country(self, value: object) -> Optional[str]:
        text = self._coerce_str(value)
        if text:
            return text[:2].upper()
        return None

    def _merge_metadata(
        self,
        selected: Sequence[SimilarArticle],
        lookup: Mapping[Tuple[str, Optional[str]], Mapping[str, object]],
    ) -> List[Dict[str, object]]:
        enriched: List[Dict[str, object]] = []
        for article in selected:
            metadata = lookup.get(self._article_key(article), {})
            enriched.append(
                {
                    "baslik": metadata.get("baslik"),
                    "ozet": metadata.get("ozet"),
                    "url": article.url or metadata.get("url"),
                    "kaynak": article.source_name or metadata.get("kaynak"),
                    "kaynak_id": article.source_id,
                    "tarih": self._format_datetime(article.published_at),
                    "ulke": article.country_code or metadata.get("ulke"),
                    "benzerlik": round(article.similarity, 4),
                    "guvenilirlik": round(article.credibility, 4),
                }
            )
        return enriched

    @staticmethod
    def _article_key(article: SimilarArticle) -> Tuple[str, Optional[str]]:
        return article.source_id, article.url

    @staticmethod
    def _format_datetime(value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        if value.tzinfo is not None:
            return value.isoformat()
        return value.isoformat() + "Z"


def status_message_tr(status: VerificationStatus) -> str:
    """Map verification status to Turkish explanation."""

    if status is VerificationStatus.VERIFIED:
        return "Bu haber birden fazla güvenilir kaynak tarafından doğrulandı."
    if status is VerificationStatus.LIKELY_TRUE:
        return "Bu haber büyük ölçüde doğru görünmektedir."
    if status is VerificationStatus.UNCERTAIN:
        return "Bu haberin doğruluğu şu anda net değil."
    if status is VerificationStatus.DISPUTED:
        return "Bu haberle ilgili çelişkili veya tartışmalı bilgiler var."
    return "Bu haber için yeterli doğrulama verisi bulunamadı."


__all__ = [
    "NewsVerificationWorkflow",
    "VerificationWorkflowResult",
    "status_message_tr",
]
