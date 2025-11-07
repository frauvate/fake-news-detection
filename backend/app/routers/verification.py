"""HTTP endpoints for running news verification pipeline."""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from backend.app.core.constants import (
    ConfidenceLevel,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
    VerificationStatus,
)
from backend.app.core.exceptions import (
    InsufficientDataException,
    NoSimilarArticlesException,
    ValidationException,
    VerificationException,
)
from backend.app.services import (
    NewsVerificationWorkflow,
    status_message_tr,
)

router = APIRouter(prefix="/verification", tags=["Verification"])


class VerificationRequest(BaseModel):
    text: str = Field(..., description="Doğrulanacak haber metni")
    limit: Optional[int] = Field(None, description="Çekilecek benzer haber sayısı")


class SimilarArticleOut(BaseModel):
    baslik: Optional[str] = None
    ozet: Optional[str] = None
    url: Optional[str] = None
    kaynak: Optional[str] = None
    kaynak_id: str
    tarih: Optional[str] = None
    ulke: Optional[str] = None
    benzerlik: float
    guvenilirlik: float


class VerificationResponse(BaseModel):
    mesaj: str
    skor: float
    durum: VerificationStatus
    guven: ConfidenceLevel
    temiz_metin: str
    fallback: bool
    benzer_haberler: List[SimilarArticleOut]


_workflow = NewsVerificationWorkflow()


def get_workflow() -> NewsVerificationWorkflow:
    return _workflow


@router.post("/", response_model=VerificationResponse)
async def verify_news(
    payload: VerificationRequest = Body(...),
    workflow: NewsVerificationWorkflow = Depends(get_workflow),
):
    try:
        result = workflow.verify_text(payload.text, limit=payload.limit)
    except ValidationException as exc:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail={"message": exc.message, "code": exc.error_code, "details": exc.details},
        ) from exc
    except NoSimilarArticlesException as exc:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail={"message": exc.message, "code": exc.error_code, "details": exc.details},
        ) from exc
    except InsufficientDataException as exc:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail={"message": exc.message, "code": exc.error_code, "details": exc.details},
        ) from exc
    except VerificationException as exc:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": exc.message, "code": exc.error_code, "details": exc.details},
        ) from exc

    message = status_message_tr(result.verification.status)
    return VerificationResponse(
        mesaj=message,
        skor=result.verification.score,
        durum=result.verification.status,
        guven=result.verification.confidence,
        temiz_metin=result.clean_text,
        fallback=result.fallback_used,
        benzer_haberler=[SimilarArticleOut(**article) for article in result.articles],
    )
