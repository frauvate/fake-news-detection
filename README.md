# 📰 Fake News Crawler System

Bu proje, **Türkçe haber sitelerinden** (Sözcü, BBC Türkçe, Sputnik, NTV, Hürriyet) haberleri toplayan, temizleyen ve **MongoDB veritabanına kaydeden** bir otomatik haber toplama sistemidir.

## 🚀 Özellikler

- ✅ RSS destekli sitelerden otomatik veri çekme  
- 🧠 Manuel crawler desteği (örnek: Hürriyet)  
- 🧩 Duplicate (tekrar eden haber) kontrolü  
- 🤖 `robots.txt` uyumlu tarama  
- 🧾 Otomatik log kaydı (her çekim için)  
- 🕒 Windows Task Scheduler ile **otomatik saatlik çalıştırma**  
- 💾 MongoDB veritabanı desteği

---

## 🏗️ Proje Yapısı

fake-news-crawler/
│
├── crawl_all.py # Ana dosya - tüm crawlerları çalıştırır
├── crawl_with_rss.py # RSS kaynaklarını çeken crawler
├── manual_crawlers/
│ ├── hurriyet.py # Manuel Hürriyet crawler
│ ├── sozcu.py # Manuel Sözcü crawler (isteğe bağlı)
│ ├── ntv.py # Manuel NTV crawler (isteğe bağlı)
│ └── init.py
├── config.py # Veritabanı bağlantı ayarları (git'e dahil edilmez)
├── requirements.txt # Gerekli kütüphaneler
├── stats.py # Veritabanı istatistiklerini gösterir
└── .gitignore


---

## ⚙️ Kurulum

### 1️⃣ Ortam Hazırlığı
```bash
git clone https://github.com/frauvate/fake-news-detection.git
cd fake-news-crawler
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
