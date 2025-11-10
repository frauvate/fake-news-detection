<p align="center">
  <img src="https://ibb.co/8DW9YCky" alt="logo" width="200"/>
</p>

<h1 align="center">📰 VEERIFY </h1>
<p align="center">kaynak taraması yaparak haber doğruluğunu analiz eden veri odaklı sistem</p>

---

## 🚀 Proje Hakkında
**Veerify**, sahte haberleri tespit etmeye ve güvenilirlik skorunu hesaplamaya odaklanmış bir web tabanlı sistemdir.  
Sistem, bir haber metnini girdi olarak alır, farklı kaynaklardan benzer içerikleri bulur ve **doğruluk olasılığı** sunar.  
Ayrıca kullanıcıların yaptığı sorgular üzerinden **trend analizi** gerçekleştirir.

---

## 🧠 Genel Özellikler
- 🔍 **Kaynak bazlı doğruluk tespiti** (birden fazla güvenilir siteden arama)
- 📊 **Trend analizi** (en çok konuşulan konular)
- 💾 **Redis cache** ile hızlı sorgu sonuçları
- 📚 **MongoDB Atlas Search** ile semantik arama
- 👥 **Kullanıcı kayıt ve geçmiş sorgu yönetimi**
- ⚙️ **Arka plan veri toplayıcı (crawler) ve model pipeline**

---

## 🧩 Tech Stack

<p align="center">
  <!-- Backend -->
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40" alt="Python"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" width="40" height="40" alt="FastAPI"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="40" height="40" alt="PostgreSQL"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg" width="40" height="40" alt="MongoDB"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/redis/redis-original.svg" width="40" height="40" alt="Redis"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/react/react-original.svg" width="40" height="40" alt="React"/>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/git/git-original.svg" width="40" height="40" alt="Git"/>
</p>

<p align="center">
  
  <b>Backend:</b> FastAPI, Python • 
  <b>Frontend:</b> React • 
  <b>Database:</b> PostgreSQL, MongoDB • 
  <b>Cache:</b> Redis • 
</p>

---

## 🧮 Sistem Akışı
1. Kullanıcı haber metnini sisteme girer.  
2. Backend, haber içeriğini temizleyip embedding oluşturur.  
3. MongoDB Atlas Search veya OpenSearch üzerinden benzer haberleri arar.  
4. Sonuçlar:
   - Benzer haber sayısı  
   - Kaynak çeşitliliği  
   - Güvenilirlik skoru  
   şeklinde hesaplanır.
5. ML modeli trendleri analiz eder, Redis üzerinde cache’ler.
6. Kullanıcı geçmiş sorgularını ve trendleri görebilir.

---

## 🧑‍💻 Ekip

<p align="center">
  <table>
    <tr>
      <td align="center" width="200">
        <img src="https://avatars.githubusercontent.com/u/frauvate?s=200" width="100" height="100" style="border-radius:50%;" alt="Esma Asyldrm"/><br>
        <b>Esma Asyldrm</b><br>
        Trend Analizi & Sistem Tasarımı<br>
        <a href="https://github.com/frauvate">GitHub</a>
      </td>
      <td align="center" width="200">
        <img src="https://avatars.githubusercontent.com/u/member2_id?s=200" width="100" height="100" style="border-radius:50%;" alt="Üye 2"/><br>
        <b>Üye 2</b><br>
        Backend Geliştirici<br>
        <a href="https://github.com/member2">GitHub</a>
      </td>
      <td align="center" width="200">
        <img src="https://avatars.githubusercontent.com/u/member3_id?s=200" width="100" height="100" style="border-radius:50%;" alt="Üye 3"/><br>
        <b>Üye 3</b><br>
        Veri Toplama & Crawler<br>
        <a href="https://github.com/member3">GitHub</a>
      </td>
      <td align="center" width="200">
        <img src="https://avatars.githubusercontent.com/u/member4_id?s=200" width="100" height="100" style="border-radius:50%;" alt="Üye 4"/><br>
        <b>Üye 4</b><br>
        Veritabanı & Docker Setup<br>
        <a href="https://github.com/member4">GitHub</a>
      </td>
    </tr>
  </table>
</p>

---

## 🎓 Danışman
**Doç. Dr. Özal YILDIRIM**  
Fırat Üniversitesi – Yazılım Mühendisliği Bölümü
&&
**Araş. Gör. Çağrı ŞAHİN**  
Fırat Üniversitesi – Yazılım Mühendisliği Bölümü

---

<p align="center">💡 Gerçekleri görünür kılmak için geliştirilmiştir.</p>
