"""
Sözcü Manuel Crawler
--------------------
RSS'i çalışmadığı için HTML parsing ile haberleri çeker.
"""

import requests
from selectolax.parser import HTMLParser
from datetime import datetime
from urllib.parse import urljoin
import sys
import os

# Ana klasörü Python path'ine ekle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from config import REQUEST_TIMEOUT, USER_AGENT
except:
    REQUEST_TIMEOUT = 10
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def crawl_sozcu():
    """
    Sözcü anasayfasından haberleri çeker
    
    Returns:
        list: Haber listesi (dict'lerden oluşan)
    """
    print("\n  🔍 https://www.sozcu.com.tr/")
    print("     └─ HTML parsing ile çekiliyor...")
    
    base_url = "https://www.sozcu.com.tr"
    haberler = []
    
    try:
        # User-Agent ekleyerek istek at
        headers = {"User-Agent": USER_AGENT}
        
        response = requests.get(base_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # HTML'i parse et
        tree = HTMLParser(response.text)
        
        # Tüm linkleri tara
        goruldu = set()  # Duplicate kontrolü için
        
        for link_element in tree.css("a"):
            href = link_element.attributes.get("href", "")
            
            # Boş link atla
            if not href:
                continue
            
            # Absolute URL yap
            if not href.startswith("http"):
                href = urljoin(base_url, href)
            
            # Sadece sozcu.com.tr domain'inden al
            if "sozcu.com.tr" not in href:
                continue
            
            # Duplicate kontrolü
            if href in goruldu:
                continue
            
            # Ana sayfa, kategori sayfaları vb. atla - sadece haber detay sayfaları
            # Sözcü'de haberler genelde sayı ile biten URL'lerde
            if not any(char.isdigit() for char in href.split('/')[-1]):
                continue
            
            # Başlık al
            baslik = link_element.text(strip=True)
            
            # Eğer başlık link içinde yoksa, title attribute'dan al
            if not baslik:
                baslik = link_element.attributes.get("title", "")
            
            # Çok kısa başlıkları atla
            if not baslik or len(baslik) < 10:
                continue
            
            # Haber objesi oluştur
            haber = {
                "baslik": baslik.strip(),
                "ozet": None,
                "tarih": datetime.now(),
                "kaynak": "sozcu",
                "url": href
            }
            
            haberler.append(haber)
            goruldu.add(href)
            
            # Limit
            if len(haberler) >= 50:
                break
        
        print(f"     └─ ✅ {len(haberler)} haber bulundu")
        
    except requests.Timeout:
        print(f"     └─ ⏱️  Timeout!")
    except requests.RequestException as e:
        print(f"     └─ ❌ HTTP hatası: {e}")
    except Exception as e:
        print(f"     └─ ❌ Beklenmeyen hata: {e}")
    
    return haberler


if __name__ == "__main__":
    # Test için
    haberler = crawl_sozcu()
    print(f"\n✅ Test tamamlandı. {len(haberler)} haber bulundu.")
    if haberler:
        print("\nİlk 3 haber:")
        for i, haber in enumerate(haberler[:3], 1):
            print(f"\n{i}. Başlık: {haber['baslik']}")
            print(f"   URL: {haber['url']}")