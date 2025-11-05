# test_db.py
from sqlalchemy import create_engine, text

print("Başlatılıyor...")

# SQLite kullanıyoruz
engine = create_engine("sqlite:///./test.db")

try:
    with engine.connect() as conn:
        print("Bağlantı nesnesi oluşturuldu:", engine)
        result = conn.execute(text("SELECT 1")).fetchall()
        print("Test sorgusu sonucu:", result)
except Exception as e:
    print("Hata:", e)
