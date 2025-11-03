"""
MongoDB bağlantısını test eden basit script
"""

from pymongo import MongoClient
from config import MONGO_CONNECTION_STRING, VERITABANI_ADI

try:
    # MongoDB'ye bağlan
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client[VERITABANI_ADI]
    
    # Bağlantıyı test et
    print("🔍 MongoDB'ye bağlanılıyor...")
    client.server_info()  # Bağlantıyı test eder
    
    print("✅ MongoDB bağlantısı başarılı!")
    print(f"📁 Mevcut koleksiyonlar: {db.list_collection_names()}")
    
except Exception as e:
    print(f"❌ MongoDB bağlantı hatası: {e}")
    print("💡 config.py dosyasındaki bağlantı bilgilerini kontrol et")