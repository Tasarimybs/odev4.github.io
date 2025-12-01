# Elektronik Mağazası Flask Web Uygulaması

Bu proje, Flask ve SQLAlchemy kullanılarak geliştirilmiş bir elektronik mağazası web uygulamasıdır. Ürünler, kategoriler, sepet ve iletişim mesajları dinamik olarak veritabanında saklanır ve yönetici paneli üzerinden kontrol edilebilir.

## Özellikler
- Ana sayfa: Ürünleri listeler
- Sepet: Ürün ekleme/silme ve toplam tutar
- Hakkımızda: Firma bilgileri
- İletişim: Mesaj gönderme ve admin panelinde görüntüleme
- Yönetici paneli: Ürün ekleme, silme, fiyat güncelleme, mesajları görme

## Kurulum
1. Gerekli paketleri yükleyin:
   ```bash
   pip install flask flask_sqlalchemy
   ```
2. Uygulamayı başlatın:
   ```bash
   python elektro.py
   ```
3. Tarayıcıda açın:
   - Ana sayfa: http://127.0.0.1:5000/
   - Yönetici paneli: http://127.0.0.1:5000/admin
   - Mesajlar: http://127.0.0.1:5000/admin/mesajlar

## Dosya Yapısı
- `elektro.py`: Ana uygulama dosyası
- `templates/`: HTML şablonları
- `instance/site.db`: SQLite veritabanı

## Notlar
- İlk çalıştırmada veritabanı ve örnek veriler otomatik oluşturulur.
- Tüm işlemler dinamik olarak veritabanı üzerinden yapılır.

---
Bu proje eğitim ve demo amaçlıdır.