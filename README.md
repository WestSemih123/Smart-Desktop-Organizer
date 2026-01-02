# 📂 Smart Desktop Organizer v5.0

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat&logo=windows)

**Smart Desktop Organizer**, masaüstünüzü ve indirilenler klasörünüzü otomatik olarak düzenleyen, modern arayüze sahip, Python tabanlı gelişmiş bir otomasyon aracıdır. Karmaşık dosya yığınlarını saniyeler içinde kategorize eder ve size zaman kazandırır.

---

## 🚀 Özellikler

Bu proje **v5.0** sürümüyle aşağıdaki yeteneklere sahiptir:

* **📂 Çoklu Klasör Takibi:** İndirilenler, Masaüstü veya seçtiğiniz herhangi bir klasörü aynı anda izler.
* **☁️ Bulut Yedekleme:** Dosyaları düzenlerken otomatik olarak Google Drive veya OneDrive klasörünüze yedekler.
* **🎨 Modern Arayüz:** CustomTkinter ile geliştirilmiş, **Dark Mode** destekli şık ayarlar menüsü.
* **⚡ Otomatik Başlatma:** Windows başlangıcında sessizce çalışmaya başlar (System Tray entegrasyonu).
* **📦 Akıllı Zip Açıcı:** İndirilen `.zip` dosyalarını otomatik olarak ilgili klasöre çıkartır.
* **↩️ Geri Alma (Undo):** Yanlış taşınan dosyaları tek tıkla geri alır.
* **📊 İstatistikler:** Hangi türden kaç dosya düzenlendiğini ve kazanılan zamanı raporlar.
* **📜 Canlı Log:** Yapılan işlemleri anlık olarak arayüzden izleyebilirsiniz.

---

## 🛠️ Kurulum

Projeyi bilgisayarınıza klonlayın ve gerekli kütüphaneleri yükleyin.

```bash
# Repoyu klonlayın
git clone [https://github.com/KULLANICI_ADINIZ/Smart-Desktop-Organizer.git](https://github.com/KULLANICI_ADINIZ/Smart-Desktop-Organizer.git)

# Proje dizinine girin
cd Smart-Desktop-Organizer

# Gereksinimleri yükleyin
pip install -r requirements.txt
▶️ Kullanım
Uygulamayı başlatmak için terminalden şu komutu çalıştırın:

Bash

python main.py
Uygulama başladığında System Tray (Saatin yanındaki simgeler) kısmına yerleşir. Arka planda sessizce çalışır.

Sağ Tık Menüsü: Ayarlar, Geri Al ve Çıkış seçeneklerine buradan ulaşabilirsiniz.

Ayarlar: Kuralları değiştirebilir, yeni izlenecek klasörler ekleyebilir (.odp, .jpg vb.) ve istatistikleri görebilirsiniz.

⚙️ Yapılandırma
Program ilk açılışta bir settings.json dosyası oluşturur. Arayüz üzerinden şunları kolayca yönetebilirsiniz:

Dosya Kuralları: Hangi uzantının (Örn: .pdf, .odp, .jpg, .mp4) hangi alt klasöre taşınacağını belirleyin.

Tema: Dark / Light mod seçimi yapın.

Ekstra Özellikler: Otomatik temizlik, tarih bazlı klasörleme vb. seçenekleri açıp kapatın.

🏗️ Kullanılan Teknolojiler
Python 3: Ana programlama dili.

Watchdog: Dosya sistemi olaylarını canlı izlemek için.

CustomTkinter: Modern GUI arayüzü için.

Pystray: Arka planda (System Tray) çalışmak için.

Plyer: Masaüstü bildirimleri için.

🤝 Katkıda Bulunma
Pull request'ler kabul edilir. Büyük değişiklikler için önce lütfen bir tartışma (issue) başlatın. Her türlü katkıya açığız!

📄 Lisans
Bu proje MIT lisansı ile lisanslanmıştır.