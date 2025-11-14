# Araç Tanıma Mobil Uygulaması

Flutter ile geliştirilmiş yapay zeka destekli araç marka/model, plaka ve renk tanıma mobil uygulaması.

## Özellikler

- **Araç Marka/Model Tanıma**: TensorFlow Lite CNN modeli ile otomatik araç tanıma
  - 2012-2014 Ford Focus (Ön/Arka)
  - 2016-2019 Honda Civic (Ön/Arka)

- **Plaka Okuma**: Google ML Kit OCR ile Türk plaka formatı okuma

- **Renk Tespiti**: RGB analizi ile araç rengi belirleme
  - Beyaz, Siyah, Gri, Füme, Lacivert, Kırmızı

- **Veritabanı Kontrolü**: SQLite ile kayıtlı araç bilgilerini kontrol etme

- **Kamera ve Galeri Desteği**: Gerçek zamanlı fotoğraf çekme veya galeriden seçme

## Teknolojiler

- **Flutter**: Cross-platform mobil uygulama framework
- **TensorFlow Lite**: Mobil cihazlarda makine öğrenmesi
- **Google ML Kit**: OCR (Optical Character Recognition)
- **SQLite**: Yerel veritabanı
- **Provider**: State management

## Kurulum

### Gereksinimler

- Flutter SDK (>=3.0.0)
- Android Studio veya Xcode
- Python 3.8+ (model dönüştürme için)

### Adımlar

1. **Projeyi klonlayın**
   ```bash
   git clone <repository-url>
   cd Vehicle-brand-model-recognition-with-deep-learning-using-keras
   ```

2. **Model dosyasını indirin**

   Model dosyasını aşağıdaki linkten indirin:
   https://drive.google.com/file/d/1rbViqZiql7gtXUHZq-Qp6GhwdlEkS2-N/view?usp=sharing

   İndirilen `model_600_450_32_categorical.h5` dosyasını proje ana dizinine yerleştirin.

3. **Modeli TensorFlow Lite formatına dönüştürün**
   ```bash
   pip install tensorflow numpy keras
   python convert_model_to_tflite.py
   ```

   Bu komut:
   - `.h5` modelini `.tflite` formatına dönüştürür
   - `flutter_app/assets/models/model.tflite` dosyasını oluşturur
   - `flutter_app/assets/models/labels.txt` etiket dosyasını oluşturur

4. **Flutter bağımlılıklarını yükleyin**
   ```bash
   cd flutter_app
   flutter pub get
   ```

5. **Uygulamayı çalıştırın**
   ```bash
   # Android için
   flutter run

   # iOS için (Mac gerekli)
   flutter run -d ios
   ```

## Proje Yapısı

```
flutter_app/
├── lib/
│   ├── main.dart                 # Ana uygulama giriş noktası
│   ├── models/
│   │   └── vehicle.dart          # Veri modelleri
│   ├── screens/
│   │   ├── home_screen.dart      # Ana sayfa
│   │   └── recognition_screen.dart # Tanıma sonuç ekranı
│   └── services/
│       ├── model_service.dart           # TFLite model servisi
│       ├── color_detection_service.dart # Renk tespit servisi
│       ├── plate_recognition_service.dart # Plaka okuma servisi
│       └── database_service.dart        # Veritabanı servisi
├── assets/
│   └── models/
│       ├── model.tflite          # TensorFlow Lite modeli
│       └── labels.txt            # Model etiketleri
├── android/                      # Android platform kodu
├── ios/                          # iOS platform kodu
└── pubspec.yaml                  # Flutter bağımlılıkları
```

## Kullanım

1. Uygulamayı açın
2. "Kamera ile Çek" veya "Galeriden Seç" butonuna basın
3. Araç fotoğrafı seçin veya çekin
4. Uygulama otomatik olarak:
   - Araç marka/modelini tespit eder
   - Rengi analiz eder
   - Plakayı okur
   - Veritabanında eşleşme kontrolü yapar
5. Sonuçları görüntüleyin

## Veritabanı Yönetimi

Uygulama otomatik olarak örnek araç kayıtları ile başlar:

- 34ABC123 - 2012_2014_Ford Focus - Beyaz
- 06XYZ456 - 2016_2019_Honda Civic - Siyah
- 35TEST99 - 2012_2014_Ford Focus - Kırmızı

Yeni kayıt eklemek için `database_service.dart` dosyasındaki `insertVehicle()` metodunu kullanabilirsiniz.

## Model Detayları

### CNN Mimarisi
- Input: 600x450x3 (RGB görüntü)
- 3x Convolutional + MaxPooling katmanları
- Flatten + Dense katmanlar
- Output: 4 sınıf (softmax)

### Model Performansı
- Training accuracy: ~95%+
- Validation accuracy: ~90%+
- Model boyutu: ~10-15 MB (TFLite)

## İzinler

### Android
- `CAMERA`: Kamera erişimi
- `READ_EXTERNAL_STORAGE`: Galeriden görüntü okuma
- `INTERNET`: ML Kit için

### iOS
- `NSCameraUsageDescription`: Kamera kullanım açıklaması
- `NSPhotoLibraryUsageDescription`: Fotoğraf kütüphanesi erişimi

## Sorun Giderme

### Model yüklenmiyor
- `assets/models/model.tflite` dosyasının var olduğundan emin olun
- `pubspec.yaml` dosyasında assets yolunun doğru olduğunu kontrol edin
- `flutter clean && flutter pub get` komutunu çalıştırın

### Kamera açılmıyor
- Cihaz izinlerini kontrol edin
- `AndroidManifest.xml` dosyasında izinlerin tanımlı olduğunu doğrulayın

### Plaka okumuyor
- Görüntünün net ve ışıklı olduğundan emin olun
- Plaka bölgesinin görüntüde net görüldüğünden emin olun

## Geliştirme Notları

### Yeni Araç Modeli Ekleme

1. Yeni modeli eğitin (training_set'e yeni sınıf ekleyin)
2. Modeli yeniden dönüştürün
3. `labels.txt` dosyasını güncelleyin
4. `model_service.dart` dosyasındaki sınıf sayısını güncelleyin

### Performans Optimizasyonu

- Model boyutunu küçültmek için quantization kullanabilirsiniz
- Görüntü boyutunu azaltarak işlem hızını artırabilirsiniz
- Background processing için isolate kullanabilirsiniz

## Lisans

Bu proje eğitim amaçlıdır. Kişisel verilerin gizliliğine dikkat edilmelidir.

## İletişim

Sorular ve öneriler için issue açabilirsiniz.

## Teşekkürler

- TensorFlow Lite ekibine
- Google ML Kit ekibine
- Flutter topluluğuna
