"""
RSS Feed Crawler
-----------------
RSS destekli haber sitelerinden (Sözcü, BBC Türkçe, Sputnik, NTV) 
haberleri çekip MongoDB'ye kaydeder.

Özellikler:
- robots.txt kontrolü
- Duplicate kontrolü (aynı haber 2 kez kaydedilmez)
- Detaylı log tutma
- Hata yönetimi
"""

import feedparser
from pymongo import MongoClient
from datetime import datetime
from selectolax.parser import HTMLParser
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import requests

from config import (
    MONGO_CONNECTION_STRING, 
    VERITABANI_ADI, 
    HABERLER_KOLEKSIYONU, 
    LOG_KOLEKSIYONU,
    REQUEST_TIMEOUT,
    REQUEST_DELAY,
    USER_AGENT
)

# RSS Feed Kaynakları
# Her site için birden fazla kategori ekleyerek daha fazla haber toplanır
RSS_FEEDS = {
    "sozcu": [
        "https://www.sozcu.com.tr/feed/",
        "https://www.sozcu.com.tr/kategori/gundem/feed/",
        "https://www.sozcu.com.tr/kategori/ekonomi/feed/",
        "https://www.sozcu.com.tr/kategori/dunya/feed/",
        "https://www.sozcu.com.tr/kategori/spor/feed/",
    ],
    "bbc": [
        "https://feeds.bbci.co.uk/turkce/rss.xml",
    ],
    "sputnik": [
        "https://tr.sputniknews.com/export/rss2/archive/index.xml",
    ],
    "ntv": [
        "https://www.ntv.com.tr/gundem.rss",
        "https://www.ntv.com.tr/ekonomi.rss",
        "https://www.ntv.com.tr/dunya.rss",
        "https://www.ntv.com.tr/turkiye.rss",
        "https://www.ntv.com.tr/teknoloji.rss",
        "https://www.ntv.com.tr/egitim.rss",
        "https://www.ntv.com.tr/saglik.rss",
        "https://www.ntv.com.tr/yasam.rss",
    ]
}


def html_temizle(html_metin):
    """
    HTML etiketlerini temizleyip saf metni döndürür
    
    Args:
        html_metin (str): HTML içeren metin
    
    Returns:
        str: Temizlenmiş metin veya None
    """
    if not html_metin:
        return None
    try:
        parser = HTMLParser(html_metin)
        temiz_metin = parser.text().strip()
        return temiz_metin if temiz_metin else None
    except Exception as e:
        return None


def robots_txt_kontrol(url):
    """
    Verilen URL'nin robots.txt'ine göre erişilebilir olup olmadığını kontrol eder
    
    Args:
        url (str): Kontrol edilecek URL
    
    Returns:
        bool: Erişim izni varsa True, yoksa False
    """
    try:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        rp = RobotFileParser()
        rp.set_url(f"{base_url}/robots.txt")
        rp.read()
        
        # User-agent olarak '*' kullanıyoruz (genel bot)
        izin = rp.can_fetch("*", url)
        return izin
    except Exception as e:
        # Hata durumunda güvenli tarafta kal, izin var say
        print(f"    ⚠️  robots.txt kontrol hatası: {e}")
        return True


def tarih_parse(entry):
    """
    RSS entry'sinden tarihi parse eder
    
    Args:
        entry: feedparser entry objesi
    
    Returns:
        datetime: Parse edilmiş tarih veya şimdiki zaman
    """
    # Önce published, sonra updated alanlarını kontrol et
    tarih_str = getattr(entry, "published", None) or getattr(entry, "updated", None)
    
    if tarih_str:
        try:
            # published_parsed veya updated_parsed varsa kullan
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                return datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                return datetime(*entry.updated_parsed[:6])
        except Exception as e:
            pass
    
    # Parse edilemezse şimdiki zamanı kullan
    return datetime.now()


def rss_cek(rss_url, kaynak_adi, collection, log_collection):
    """
    Belirtilen RSS feed'den haberleri çeker ve MongoDB'ye kaydeder
    
    Args:
        rss_url (str): RSS feed URL'i
        kaynak_adi (str): Kaynak adı (örn: "sozcu")
        collection: MongoDB articles koleksiyonu
        log_collection: MongoDB logs koleksiyonu
    
    Returns:
        dict: Log bilgileri
    """
    baslangic_zamani = time.time()
    
    # Log objesi oluştur
    log = {
        "cekim_zamani": datetime.now(),
        "kaynak": kaynak_adi,
        "endpoint": rss_url,
        "basarili": False,
        "durum": "fail",  # basarili/fail/timeout
        "hata_mesaji": None,
        "cekilen_haber_sayisi": 0,
        "sure_saniye": None
    }
    
    try:
        print(f"\n  🔍 {rss_url}")
        print(f"     └─ Çekiliyor...")
        
        # robots.txt kontrolü
        if not robots_txt_kontrol(rss_url):
            log["hata_mesaji"] = "robots.txt tarafından engellenmiş"
            log["durum"] = "fail"
            print(f"     └─ ❌ robots.txt izin vermiyor!")
            return log
        
        # RSS feed'i parse et (timeout ile)
        try:
            # feedparser timeout desteklemiyor, requests ile önce çekelim
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(rss_url, headers=headers, timeout=REQUEST_TIMEOUT)
            feed = feedparser.parse(response.content)
        except requests.Timeout:
            log["hata_mesaji"] = "Timeout - Bağlantı zaman aşımına uğradı"
            log["durum"] = "timeout"
            print(f"     └─ ⏱️  Timeout!")
            return log
        except Exception as e:
            log["hata_mesaji"] = f"İstek hatası: {str(e)}"
            log["durum"] = "fail"
            print(f"     └─ ❌ İstek hatası!")
            return log
        
        # Feed'de hata var mı kontrol et
        if feed.bozo:
            log["hata_mesaji"] = f"RSS parse hatası: {getattr(feed, 'bozo_exception', 'Bilinmeyen hata')}"
            log["durum"] = "fail"
            print(f"     └─ ❌ RSS parse hatası!")
            return log
        
        # Haber yoksa
        if not feed.entries:
            log["hata_mesaji"] = "RSS feed'inde haber bulunamadı"
            log["durum"] = "fail"
            print(f"     └─ ⚠️  Haber bulunamadı!")
            return log
        
        # Haberleri işle
        eklenen_sayi = 0
        taranan_sayi = len(feed.entries)
        
        for entry in feed.entries:
            # Gerekli alanları al
            baslik = getattr(entry, "title", None)
            link = getattr(entry, "link", None)
            ozet_html = getattr(entry, "summary", None) or getattr(entry, "description", None)
            ozet = html_temizle(ozet_html)
            tarih = tarih_parse(entry)
            
            # Link yoksa atla
            if not link:
                continue
            
            # Başlık yoksa atla
            if not baslik or len(baslik.strip()) < 5:
                continue
            
            # Haber objesi oluştur
            haber = {
                "baslik": baslik.strip(),
                "ozet": ozet,
                "tarih": tarih,
                "kaynak": kaynak_adi,
                "url": link,
                "eklenme_zamani": datetime.now()
            }
            
            # Aynı URL zaten varsa atla (duplicate kontrolü)
            if collection.find_one({"url": link}):
                continue
            
            # MongoDB'ye kaydet
            try:
                collection.insert_one(haber)
                eklenen_sayi += 1
            except Exception as e:
                # Unique index hatası veya başka bir hata
                pass
        
        # Başarılı
        log["basarili"] = True
        log["durum"] = "basarili"
        log["cekilen_haber_sayisi"] = eklenen_sayi
        print(f"     └─ ✅ {eklenen_sayi}/{taranan_sayi} yeni haber eklendi")
        
    except Exception as e:
        log["hata_mesaji"] = str(e)
        log["durum"] = "fail"
        print(f"     └─ ❌ Beklenmeyen hata: {e}")
    
    finally:
        # Süreyi hesapla
        log["sure_saniye"] = round(time.time() - baslangic_zamani, 2)
        
        # Log'u kaydet
        try:
            log_collection.insert_one(log)
        except Exception as e:
            print(f"     └─ ⚠️  Log kaydedilemedi: {e}")
    
    return log


def rss_crawler_calistir():
    """
    Ana fonksiyon - Tüm RSS kaynaklarını çeker
    
    Returns:
        dict: Özet istatistikler
    """
    print("=" * 80)
    print("🌐 RSS CRAWLER BAŞLATILIYOR")
    print("=" * 80)
    
    # MongoDB'ye bağlan
    try:
        client = MongoClient(MONGO_CONNECTION_STRING)
        db = client[VERITABANI_ADI]
        articles = db[HABERLER_KOLEKSIYONU]
        logs = db[LOG_KOLEKSIYONU]
        
        print(f"\n✅ MongoDB bağlantısı başarılı!")
        print(f"📁 Veritabanı: {VERITABANI_ADI}")
        
        # İndeksler oluştur (ilk çalıştırmada)
        try:
            articles.create_index("url", unique=True)
            articles.create_index("kaynak")
            articles.create_index("tarih")
            print("✅ Veritabanı indeksleri hazır")
        except:
            pass  # Zaten varsa hata vermesin
        
        print(f"📊 Mevcut haber sayısı: {articles.count_documents({})}")
        
    except Exception as e:
        print(f"❌ MongoDB bağlantı hatası: {e}")
        return None
    
    # Toplam istatistikler
    toplam_cekilen = 0
    toplam_basarili = 0
    toplam_basarisiz = 0
    toplam_timeout = 0
    
    # Her RSS feed için
    for kaynak_adi, feed_listesi in RSS_FEEDS.items():
        print(f"\n{'=' * 80}")
        print(f"📡 {kaynak_adi.upper()} ({len(feed_listesi)} feed)")
        print(f"{'=' * 80}")
        
        for rss_url in feed_listesi:
            # RSS'i çek
            log = rss_cek(rss_url, kaynak_adi, articles, logs)
            
            # İstatistikleri güncelle
            if log["basarili"]:
                toplam_basarili += 1
                toplam_cekilen += log["cekilen_haber_sayisi"]
            elif log["durum"] == "timeout":
                toplam_timeout += 1
            else:
                toplam_basarisiz += 1
            
            # Rate limiting (siteye aşırı yük bindirmemek için bekle)
            time.sleep(REQUEST_DELAY)
    
    # Özet rapor
    print(f"\n{'=' * 80}")
    print("📊 RSS CRAWLER ÖZET RAPOR")
    print(f"{'=' * 80}")
    print(f"✅ Başarılı çekimler:    {toplam_basarili}")
    print(f"❌ Başarısız çekimler:   {toplam_basarisiz}")
    print(f"⏱️  Timeout:              {toplam_timeout}")
    print(f"📰 Bu çalışmada eklenen: {toplam_cekilen} haber")
    print(f"📁 Toplam haber sayısı:  {articles.count_documents({})} haber")
    print(f"{'=' * 80}")
    
    return {
        "basarili": toplam_basarili,
        "basarisiz": toplam_basarisiz,
        "timeout": toplam_timeout,
        "eklenen": toplam_cekilen,
        "toplam": articles.count_documents({})
    }


if __name__ == "__main__":
    rss_crawler_calistir()
    print("\n✨ RSS Crawler tamamlandı!\n")
