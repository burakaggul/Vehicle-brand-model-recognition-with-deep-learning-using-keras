# Flutter Mobil Uygulama Kurulum Rehberi

Bu rehber, mevcut araç tanıma projesini Flutter mobil uygulaması olarak çalıştırmanız için gerekli adımları içerir.

## Hızlı Başlangıç

### 1. Model Dosyasını İndirin

İlk olarak eğitilmiş model dosyasını indirin:

📥 **Model İndirme Linki**: https://drive.google.com/file/d/1rbViqZiql7gtXUHZq-Qp6GhwdlEkS2-N/view?usp=sharing

İndirilen `model_600_450_32_categorical.h5` dosyasını proje ana dizinine koyun:
```
Vehicle-brand-model-recognition-with-deep-learning-using-keras/
├── model_600_450_32_categorical.h5  ← Buraya
├── flutter_app/
├── convert_model_to_tflite.py
└── ...
```

### 2. Gerekli Paketleri Yükleyin

Python bağımlılıklarını yükleyin:
```bash
pip install tensorflow numpy keras
```

### 3. Modeli Dönüştürün

```bash
python convert_model_to_tflite.py
```

✅ Bu komut başarılı olursa şunları göreceksiniz:
- Model başarıyla dönüştürüldü
- `flutter_app/assets/models/model.tflite` oluşturuldu
- `flutter_app/assets/models/labels.txt` oluşturuldu

### 4. Flutter Projesini Hazırlayın

```bash
cd flutter_app
flutter pub get
```

### 5. Uygulamayı Çalıştırın

```bash
# Android cihaz/emulator
flutter run

# Belirli bir cihazda çalıştırmak için
flutter devices          # Mevcut cihazları listele
flutter run -d <device>  # Belirli cihazda çalıştır
```

## Detaylı Kurulum

### Flutter SDK Kurulumu

Eğer Flutter SDK'sı kurulu değilse:

**Windows:**
```bash
# Chocolatey ile
choco install flutter

# Manuel kurulum
# https://docs.flutter.dev/get-started/install/windows
```

**macOS:**
```bash
# Homebrew ile
brew install flutter

# veya manuel kurulum
# https://docs.flutter.dev/get-started/install/macos
```

**Linux:**
```bash
# Snap ile
sudo snap install flutter --classic

# veya manuel kurulum
# https://docs.flutter.dev/get-started/install/linux
```

Kurulumu kontrol edin:
```bash
flutter doctor
```

### Android Kurulumu

1. **Android Studio'yu indirin ve kurun**
   - https://developer.android.com/studio

2. **Android SDK'yı yükleyin**
   ```bash
   flutter doctor --android-licenses
   ```

3. **Android Emulator oluşturun**
   - Android Studio > Tools > AVD Manager
   - Create Virtual Device
   - Bir cihaz seçin (örn: Pixel 5)
   - Sistem image indirin (Android 11+)

### iOS Kurulumu (Sadece macOS)

1. **Xcode'u yükleyin**
   ```bash
   sudo xcodebuild -license
   ```

2. **CocoaPods'u yükleyin**
   ```bash
   sudo gem install cocoapods
   ```

3. **iOS Simulator'ı başlatın**
   ```bash
   open -a Simulator
   ```

## Proje Özellikleri

### ✨ Yeni Özellikler

- 📱 **Mobil Uyumlu**: Android ve iOS desteği
- 📷 **Kamera Entegrasyonu**: Gerçek zamanlı fotoğraf çekme
- 🎨 **Modern UI**: Material Design 3
- 🗄️ **SQLite Veritabanı**: Yerel veri saklama
- 🧠 **AI Destekli**: TensorFlow Lite ile hızlı tahmin
- 🔤 **OCR**: Google ML Kit ile plaka okuma

### 📊 Karşılaştırma: Python vs Flutter

| Özellik | Python (Orijinal) | Flutter (Mobil) |
|---------|------------------|-----------------|
| Platform | Desktop | Android/iOS |
| Kamera | Dosyadan okuma | Gerçek zamanlı |
| Model | Keras (.h5) | TFLite (.tflite) |
| OCR | Tesseract | ML Kit |
| UI | OpenCV Window | Modern Material UI |
| Boyut | ~100 MB+ | ~20-30 MB (APK) |

## Test Etme

### Test Görüntüleri

Örnek araç görüntüleri ile test edebilirsiniz:
1. Uygulamayı açın
2. "Galeriden Seç" butonuna basın
3. Bir araç fotoğrafı seçin

### Örnek Test Senaryoları

**Senaryo 1: Kayıtlı Araç**
- Marka: Ford Focus 2012-2014
- Renk: Beyaz
- Plaka: 34ABC123
- Beklenen: ✅ Eşleşme başarılı

**Senaryo 2: Kayıtsız Araç**
- Marka: Honda Civic 2016-2019
- Renk: Mavi
- Plaka: 99XXX999
- Beklenen: ❌ Eşleşme başarısız

## Sorun Giderme

### Hata: "Unable to load asset"
```bash
flutter clean
flutter pub get
flutter run
```

### Hata: "MissingPluginException"
```bash
cd flutter_app
flutter pub cache repair
flutter pub get
```

### Model çok yavaş çalışıyor
- `model_service.dart` dosyasında image boyutunu azaltın
- GPU delegate kullanın (gelişmiş)

### Kamera izni hatası
AndroidManifest.xml dosyasını kontrol edin:
```xml
<uses-permission android:name="android.permission.CAMERA"/>
```

## Build Alma

### Android APK
```bash
flutter build apk --release
```
APK yolu: `build/app/outputs/flutter-apk/app-release.apk`

### Android App Bundle (Google Play için)
```bash
flutter build appbundle --release
```

### iOS (macOS gerekli)
```bash
flutter build ios --release
```

## Performans İpuçları

1. **Release modda derleyin**: `flutter run --release`
2. **Profiling**: `flutter run --profile`
3. **Boyut optimizasyonu**: `flutter build apk --split-per-abi`

## Sonraki Adımlar

- [ ] Daha fazla araç modeli ekleyin
- [ ] Gerçek zamanlı video analizi ekleyin
- [ ] Bulut veritabanı entegrasyonu (Firebase)
- [ ] Push notification desteği
- [ ] Çoklu dil desteği
- [ ] Dark mode

## Ek Kaynaklar

- 📚 [Flutter Dokümantasyonu](https://docs.flutter.dev)
- 🎓 [TensorFlow Lite Flutter](https://www.tensorflow.org/lite/guide/flutter)
- 🔍 [ML Kit](https://developers.google.com/ml-kit)
- 💾 [SQLite Flutter](https://pub.dev/packages/sqflite)

## Destek

Sorun yaşıyorsanız:
1. README.md dosyasını okuyun
2. `flutter doctor -v` çıktısını kontrol edin
3. Issue açın (log dosyaları ile birlikte)

---

**🎉 Başarılar! Artık mobil uygulamanız hazır!**
