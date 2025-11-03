"""
Hürriyet Manuel Crawler
------------------------
Hürriyet sitesinden HTML parsing ile haberleri çeker.
RSS desteği olmadığı için anasayfa ve kategori sayfalarından çekiyor.

NOT: Hürriyet'in site yapısı sık değişebilir, CSS selectorları güncellenmeli
"""

import requests
from selectolax.parser import HTMLParser
from datetime import datetime
import time
from urllib.parse import urljoin

from config import REQUEST_TIMEOUT, USER_AGENT


def crawl_hurriyet():
    """
    Hürriyet anasayfasından haberleri çeker
    
    Returns:
        list: Haber listesi (dict'lerden oluşan)
    """
    print("\n  🔍 https://www.hurriyet.com.tr/")
    print("     └─ HTML parsing ile çekiliyor...")
    
    base_url = "https://www.hurriyet.com.tr"
    haberler = []
    
    try:
        # User-Agent ekleyerek istek at
        headers = {"User-Agent": USER_AGENT}
        
        response = requests.get(base_url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        # HTML'i parse et
        tree = HTMLParser(response.text)
        
        # Hürriyet'teki haber linklerini bul
        # NOT: Site yapısı değişebilir, CSS selectorları güncel tutulmalı
        
        # Yöntem 1: Tüm haber linklerini bul
        for link_element in tree.css("a"):
            href = link_element.attributes.get("href", "")
            
            # Sadece haber linklerini al (örnek pattern)
            if not href or not any(x in href for x in ['/haber/', '/gundem/', '/ekonomi/', '/spor/']):
                continue
            
            # Başlık al (link içindeki metin veya title attribute)
            baslik = link_element.text(strip=True)
            if not baslik:
                baslik = link_element.attributes.get("title", "")
            
            # Çok kısa başlıkları atla
            if not baslik or len(baslik) < 15:
                continue
            
            # Relative URL'i absolute yap
            if not href.startswith("http"):
                href = urljoin(base_url, href)
            
            # Duplicate kontrolü (aynı URL'yi 2 kez ekleme)
            if any(h["url"] == href for h in haberler):
                continue
            
            # Haber objesi oluştur
            haber = {
                "baslik": baslik.strip(),
                "ozet": None,  # Anasayfada özet yok genelde
                "tarih": datetime.now(),
                "kaynak": "hurriyet",
                "url": href
            }
            
            haberler.append(haber)
            
            # Çok fazla haber eklenmesini önle (her çalışmada en fazla 50)
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


def hurriyet_kategorileri_cek():
    """
    Hürriyet'in farklı kategorilerinden haberleri çeker
    
    Returns:
        list: Tüm haberler
    """
    kategoriler = [
        "",  # Anasayfa
        "gundem",
        "ekonomi",
        "dunya",
        "teknoloji",
        "spor"
    ]
    
    tum_haberler = []
    
    for kategori in kategoriler:
        url = f"https://www.hurriyet.com.tr/{kategori}" if kategori else "https://www.hurriyet.com.tr"
        
        try:
            headers = {"User-Agent": USER_AGENT}
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            tree = HTMLParser(response.text)
            
            for link_element in tree.css("a"):
                href = link_element.attributes.get("href", "")
                
                if not href or '/haber/' not in href:
                    continue
                
                baslik = link_element.text(strip=True)
                if not baslik or len(baslik) < 15:
                    continue
                
                if not href.startswith("http"):
                    href = f"https://www.hurriyet.com.tr{href}"
                
                # Duplicate kontrolü
                if any(h["url"] == href for h in tum_haberler):
                    continue
                
                haber = {
                    "baslik": baslik.strip(),
                    "ozet": None,
                    "tarih": datetime.now(),
                    "kaynak": "hurriyet",
                    "url": href
                }
                
                tum_haberler.append(haber)
            
            # Rate limiting
            time.sleep(2)
            
        except Exception as e:
            print(f"     └─ ⚠️  {kategori} kategorisi hata: {e}")
            continue
    
    return tum_haberler