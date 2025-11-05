# app/core/mongo.py
from pymongo import MongoClient
from bson import ObjectId
from decouple import config

MONGO_URL = config("MONGO_URL")
client = MongoClient(MONGO_URL)

mongo_db = client["news_database"]
articles_col = mongo_db["articles"]

# ----------------------------
# ✅ MongoDB → JSON serializer
# ----------------------------
def serialize_doc(doc: dict):
    """ObjectId'leri string'e çevir ve dökümanı JSON-safe hale getir."""
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        else:
            out[k] = v
    return out

def serialize_many(docs: list):
    return [serialize_doc(d) for d in docs]


# -----------------------------------------------
# ✅ ATLAS SEARCH (Baslik + Ozet)
# -----------------------------------------------
def search_news_atlas(query: str, limit: int = 5):
    """
    Atlas Search ile başlık+özet üzerinde arama.
    Index adı: 'default'
    """
    pipeline = [
        {
            "$search": {
                "index": "default_1",
                "text": {
                    "query": query,
                    "path": ["baslik", "ozet"],
                    "fuzzy": {"maxEdits": 2, "prefixLength": 2},
                }
            }
        },
        {
            "$project": {
                "baslik": 1,
                "ozet": 1,
                "url": 1,
                "kaynak": 1,
                "tarih": 1,
                "score": {"$meta": "searchScore"}
            }
        },
        {"$sort": {"score": -1}},
        {"$limit": limit}
    ]
    return serialize_many(list(articles_col.aggregate(pipeline)))


# -----------------------------------------------
# ✅ REGEX SEARCH (Fallback)
# -----------------------------------------------
def search_news_regex(query: str, limit: int = 5):
    """
    Atlas Search yoksa basit regex fallback (case-insensitive).
    """
    import re
    rx = re.compile(re.escape(query), re.IGNORECASE)

    cursor = articles_col.find(
        {"$or": [{"baslik": rx}, {"ozet": rx}]},
        {"baslik": 1, "ozet": 1, "url": 1, "kaynak": 1, "tarih": 1}
    ).limit(limit)

    out = []
    for doc in cursor:
        doc["score"] = None
        out.append(serialize_doc(doc))

    return out
