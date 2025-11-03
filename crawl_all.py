"""
ANA CRAWLER SİSTEMİ
-------------------
Hem RSS hem manuel crawlerları çalıştırarak tüm haber sitelerinden veri toplar.

Kullanım:
    python crawl_all.py

Özellikler:
- RSS crawlerı çalıştırır (Sözcü, BBC, Sputnik, NTV)
- Manuel crawlerları çalıştırır (Hürriyet, Sözcü)
- Tüm logları MongoDB'ye kaydeder
- Detaylı özet rapor verir  
"""

from pymongo import MongoClient
from datetime import datetime
import time

# Config dosyasından MongoDB bağlantı bilgilerini alıyoruz
from config import (
    MONGO_CONNECTION_STRING,
    VERITABANI_ADI,
    HABERLER_KOLEKSIYONU,
    LOG_KOLEKSIYONU,
)

# RSS ve manuel crawler fonksiyonları
from crawl_with_rss import rss_crawler_calistir
from manual_crawlers.hurriyet import crawl_hurriyet
from manual_crawlers.sozcu import crawl_sozcu  


def manuel_crawler_kaydet(haberler, kaynak_adi, db):
    """
    Manuel crawlerdan gelen haberleri MongoDB'ye kaydeder.

    Args:
        haberler (list): Haber listesi
        kaynak_adi (str): Kaynak adı
        db: MongoDB database objesi

    Returns:
        int: Eklenen haber sayısı
    """
    articles = db[HABERLER_KOLEKSIYONU]
    eklenen = 0

    for haber in haberler:
        # Aynı URL zaten varsa kaydetme (duplicate kontrolü)
        if articles.find_one({"url": haber["url"]}):
            continue

        try:
            articles.insert_one(haber)
            eklenen += 1
        except Exception:
            pass  # Unique index hatası olursa atla

    return eklenen


def manuel_crawlers_calistir():
    """
    Tüm manuel crawlerları çalıştırır (Hürriyet, Sözcü)
    ve sonuçları MongoDB'ye kaydeder.

    Returns:
        dict: Özet istatistikler
    """
    print("\n" + "=" * 80)
    print("🌐 MANUEL CRAWLERS BAŞLATILIYOR")
    print("=" * 80)

    # MongoDB bağlantısı
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client[VERITABANI_ADI]
        logs = db[LOG_KOLEKSIYONU]
    except Exception as e:
        print(f"❌ MongoDB bağlantı hatası: {e}")
        return None

    toplam_eklenen = 0

    # ==========================
    # 📰 HÜRRİYET
    # ==========================
    print("\n" + "=" * 80)
    print("📰 HÜRRİYET")
    print("=" * 80)

    baslangic = time.time()
    log = {
        "cekim_zamani": datetime.now(),
        "kaynak": "hurriyet",
        "endpoint": "https://www.hurriyet.com.tr/",
        "basarili": False,
        "durum": "fail",
        "hata_mesaji": None,
        "cekilen_haber_sayisi": 0,
        "sure_saniye": None,
    }

    try:
        # Hürriyet haberlerini çek
        haberler = crawl_hurriyet()

        # MongoDB'ye kaydet
        eklenen = manuel_crawler_kaydet(haberler, "hurriyet", db)

        log["basarili"] = True
        log["durum"] = "basarili"
        log["cekilen_haber_sayisi"] = eklenen
        toplam_eklenen += eklenen

    except Exception as e:
        log["hata_mesaji"] = str(e)
        print(f"  ❌ Hata: {e}")

    log["sure_saniye"] = round(time.time() - baslangic, 2)

    # Log kaydı
    try:
        logs.insert_one(log)
    except Exception as e:
        print(f"⚠️ Log kaydedilemedi: {e}")

    # ==========================
    # 📰 SÖZCÜ
    # ==========================
    print("\n" + "=" * 80)
    print("📰 SÖZCÜ")
    print("=" * 80)

    baslangic = time.time()
    log = {
        "cekim_zamani": datetime.now(),
        "kaynak": "sozcu",
        "endpoint": "https://www.sozcu.com.tr/",
        "basarili": False,
        "durum": "fail",
        "hata_mesaji": None,
        "cekilen_haber_sayisi": 0,
        "sure_saniye": None,
    }

    try:
        # Sözcü haberlerini çek
        haberler = crawl_sozcu()

        # MongoDB'ye kaydet
        eklenen = manuel_crawler_kaydet(haberler, "sozcu", db)

        log["basarili"] = True
        log["durum"] = "basarili"
        log["cekilen_haber_sayisi"] = eklenen
        toplam_eklenen += eklenen

    except Exception as e:
        log["hata_mesaji"] = str(e)
        print(f"  ❌ Hata: {e}")

    log["sure_saniye"] = round(time.time() - baslangic, 2)

    # Log kaydı
    try:
        logs.insert_one(log)
    except Exception as e:
        print(f"⚠️ Log kaydedilemedi: {e}")

    # Özet
    print(f"\n{'=' * 80}")
    print("📊 MANUEL CRAWLERS ÖZET")
    print(f"{'=' * 80}")
    print(f"📰 Eklenen haber: {toplam_eklenen}")
    print(f"{'=' * 80}")

    return {"eklenen": toplam_eklenen}


def main():
    """
    Ana fonksiyon - Hem RSS hem manuel crawlerları çalıştırır.
    """
    print("\n" + "🎯" * 40)
    print("🚀 FAKE NEWS CRAWLER SİSTEMİ BAŞLATILIYOR")
    print("🎯" * 40)
    print(f"⏰ Başlangıç: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    genel_baslangic = time.time()

    # 1️⃣ RSS Crawlers
    rss_sonuc = rss_crawler_calistir()

    # 2️⃣ Manuel Crawlers
    manuel_sonuc = manuel_crawlers_calistir()

    # Genel özet
    toplam_sure = round(time.time() - genel_baslangic, 2)

    print("\n" + "=" * 80)
    print("🎉 GENEL ÖZET RAPOR")
    print("=" * 80)

    if rss_sonuc:
        print(f"📡 RSS Crawler:")
        print(f"   ├─ Başarılı: {rss_sonuc['basarili']}")
        print(f"   ├─ Başarısız: {rss_sonuc['basarisiz']}")
        print(f"   ├─ Timeout: {rss_sonuc['timeout']}")
        print(f"   └─ Eklenen: {rss_sonuc['eklenen']} haber")

    if manuel_sonuc:
        print(f"📰 Manuel Crawler:")
        print(f"   └─ Eklenen: {manuel_sonuc['eklenen']} haber")

    if rss_sonuc and manuel_sonuc:
        toplam_haber = rss_sonuc["toplam"]
        bu_calisma = rss_sonuc["eklenen"] + manuel_sonuc["eklenen"]
        print(f"\n{'─' * 80}")
        print(f"📊 BU ÇALIŞMADA EKLENEN TOPLAM: {bu_calisma} haber")
        print(f"📁 VERİTABANINDAKİ TOPLAM:      {toplam_haber} haber")
        print(f"⏱️  TOPLAM SÜRE:                 {toplam_sure} saniye")

    print("=" * 80)
    print("✨ Tüm işlemler başarıyla tamamlandı!")
    print(f"⏰ Bitiş: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()