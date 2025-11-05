# app/routers/search.py
from fastapi import APIRouter, Body
from pydantic import BaseModel
# TextProcessor dosyanın path’ine göre import; seninkinde utils altındaydı:
from app.utils.text_processing import prepare_for_similarity_search
from app.core.mongo import search_news_atlas, search_news_regex

router = APIRouter(prefix="/search", tags=["News Search"])

class SearchIn(BaseModel):
    text: str
    limit: int | None = 5

@router.post("/")
async def search_news_endpoint(payload: SearchIn = Body(...)):
    # 1) Normalize et (Türkçe lower, html/url temizleme vs.)
    clean_text = prepare_for_similarity_search(payload.text)

    # 2) Atlas Search dene; hata olursa regex fallback
    try:
        results = search_news_atlas(clean_text, limit=payload.limit or 5)
    except Exception:
        results = search_news_regex(clean_text, limit=payload.limit or 5)

    return {
        "input_text": payload.text,
        "clean_text": clean_text,
        "count": len(results),
        "results": results
    }
