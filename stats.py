"""
Veritabanı İstatistikleri
-------------------------
Crawler'ın ilerleme durumunu ve istatistiklerini gösterir.

Kullanım:
    python stats.py
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from config import MONGO_CONNECTION_STRING, VERITABANI_ADI

def goster_istatistikler():
    """Veritabanı istatistiklerini gösterir"""
    
    client = MongoClient(MONGO_CONNECTION_STRING)
    db = client[VERITABANI_ADI]
    
    print("\n" + "=" * 80)
    print("📊 VERİTABANI İSTATİSTİKLERİ")
    print("=" * 80)
    
    # Toplam haber
    toplam = db.articles.count_documents({})
    print(f"\n📰 Toplam haber: {toplam:,}")
    
    # Hedef
    hedef = 1_000_000
    yuzde = (toplam / hedef) * 100
    kalan = hedef - toplam
    
    print(f"🎯 Hedefe ulaşma: %{yuzde:.2f}")
    print(f"🔢 Kalan: {kalan:,} haber")
    
    # İlerleme çubuğu
    bar_uzunluk = 50
    dolu = int(bar_uzunluk * yuzde / 100)
    bos = bar_uzunluk - dolu
    print(f"📊 [{'█' * dolu}{'░' * bos}] {yuzde:.1f}%")
    
    # Kaynak başına
    print(f"\n📋 Kaynak başına dağılım:")
    for kaynak in ["hurriyet", "sozcu", "bbc", "sputnik", "ntv"]:
        sayi = db.articles.count_documents({"kaynak": kaynak})
        oran = (sayi / toplam * 100) if toplam > 0 else 0
        print(f"   {kaynak.capitalize():12} : {sayi:6,} haber ({oran:5.1f}%)")
    
    # Son 24 saat
    bir_gun_once = datetime.now() - timedelta(days=1)
    son_24_saat = db.articles.count_documents({"eklenme_zamani": {"$gte": bir_gun_once}})
    print(f"\n⏰ Son 24 saatte eklenen: {son_24_saat:,} haber")
    
    # Son 1 saat
    bir_saat_once = datetime.now() - timedelta(hours=1)
    son_1_saat = db.articles.count_documents({"eklenme_zamani": {"$gte": bir_saat_once}})
    print(f"⏰ Son 1 saatte eklenen:  {son_1_saat:,} haber")
    
    # Günlük ortalama ile tahmini süre
    if son_24_saat > 0:
        gunluk_ort = son_24_saat
        kalan_gun = kalan / gunluk_ort
        print(f"\n📅 Bu hızla hedefe ulaşma süresi:")
        print(f"   └─ ~{int(kalan_gun)} gün ({int(kalan_gun/30)} ay)")
    
    # Toplam log sayısı
    toplam_log = db.crawler_logs.count_documents({})
    basarili_log = db.crawler_logs.count_documents({"basarili": True})
    basarisiz_log = toplam_log - basarili_log
    
    print(f"\n📋 Crawler çalışma istatistikleri:")
    print(f"   Toplam çalışma : {toplam_log}")
    print(f"   ✅ Başarılı    : {basarili_log}")
    print(f"   ❌ Başarısız   : {basarisiz_log}")
    
    # Son crawler logları
    print(f"\n📋 Son 5 crawler çalışması:")
    for log in db.crawler_logs.find().sort("cekim_zamani", -1).limit(5):
        durum = "✅" if log.get("basarili") else "❌"
        kaynak = log.get('kaynak', 'bilinmiyor')
        sayi = log.get('cekilen_haber_sayisi', 0)
        zaman = log.get('cekim_zamani', datetime.now()).strftime('%Y-%m-%d %H:%M')
        print(f"   {durum} {kaynak:12} - {sayi:3} haber - {zaman}")
    
    # En son eklenen haberler
    print(f"\n📰 En son eklenen 3 haber:")
    for haber in db.articles.find().sort("eklenme_zamani", -1).limit(3):
        kaynak = haber.get('kaynak', 'bilinmiyor')
        baslik = haber.get('baslik', 'Başlık yok')[:60]
        print(f"   [{kaynak}] {baslik}...")
    
    print("=" * 80)
    print()


if __name__ == "__main__":
    goster_istatistikler()