# Vehicle Brand/Model Recognition System v2.0
# Araç Marka/Model Tanıma Sistemi v2.0

[![Tests](https://github.com/burakaggul/Vehicle-brand-model-recognition-with-deep-learning-using-keras/workflows/Tests/badge.svg)](https://github.com/burakaggul/Vehicle-brand-model-recognition-with-deep-learning-using-keras/actions)
[![codecov](https://codecov.io/gh/burakaggul/Vehicle-brand-model-recognition-with-deep-learning-using-keras/branch/main/graph/badge.svg)](https://codecov.io/gh/burakaggul/Vehicle-brand-model-recognition-with-deep-learning-using-keras)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flutter](https://img.shields.io/badge/flutter-3.13.0-blue.svg)](https://flutter.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Deep Learning tabanlı araç marka/model tanıma, renk tespiti ve plaka okuma sistemi. Python (backend) ve Flutter (mobile) ile geliştirilmiştir.

## 🚀 Yenilikler v2.0

### ✅ **Güvenlik İyileştirmeleri**
- ✅ SQL Injection koruması (parametrize sorgular)
- ✅ Input validation
- ✅ Güvenli veritabanı işlemleri

### ✅ **Kod Kalitesi**
- ✅ Modüler yapı (color_detection, plate_recognition, vehicle_recognition, database_handler)
- ✅ Type hints ve docstrings
- ✅ PEP 8 uyumlu kod
- ✅ Error handling ve logging

### ✅ **Test Kapsamı**
- ✅ Python: %80+ test coverage
- ✅ Flutter: Comprehensive unit tests
- ✅ SQL Injection prevention tests
- ✅ Edge case testleri
- ✅ CI/CD pipeline (GitHub Actions)

### ✅ **Yeni Özellikler**
- ✅ CLI interface (argument parser)
- ✅ Batch processing
- ✅ Confidence scores
- ✅ Detailed logging
- ✅ Database statistics

---

## 📁 Proje Yapısı

```
Vehicle-brand-model-recognition/
├── python_src/                      # Python kaynak kodları
│   ├── __init__.py
│   ├── main.py                     # Ana program (CLI)
│   ├── color_detection.py          # Renk tespit modülü
│   ├── plate_recognition.py        # Plaka tanıma modülü
│   ├── vehicle_recognition.py      # Araç tanıma modülü (ML)
│   └── database_handler.py         # Veritabanı işlemleri (SQL-safe)
│
├── tests/                          # Python testleri
│   ├── unit/
│   │   ├── test_color_detection.py
│   │   ├── test_plate_recognition.py
│   │   ├── test_database_handler.py
│   │   └── test_vehicle_recognition.py
│   ├── integration/
│   ├── fixtures/
│   │   └── test_images/
│   └── conftest.py                 # Pytest yapılandırması
│
├── flutter_app/                    # Flutter mobil uygulama
│   ├── lib/
│   │   ├── services/
│   │   │   ├── model_service.dart
│   │   │   ├── color_detection_service.dart
│   │   │   ├── plate_recognition_service.dart
│   │   │   └── database_service.dart
│   │   ├── screens/
│   │   └── models/
│   └── test/
│       └── services/
│           ├── color_detection_service_test.dart
│           └── database_service_test.dart
│
├── .github/
│   └── workflows/
│       └── test.yml                # CI/CD pipeline
│
├── requirements.txt                # Python bağımlılıklar
├── pytest.ini                      # Pytest yapılandırması
├── Full_Code.py                    # Eski kod (deprecated)
├── convert_model_to_tflite.py     # Model dönüştürme
└── PROJECT_README.md              # Bu dosya
```

---

## 🛠️ Kurulum

### Python Backend

#### 1. Gereksinimler
```bash
Python 3.9+
Tesseract OCR
```

#### 2. Tesseract OCR Kurulumu

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-tur
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Windows:**
- [Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki) indir ve yükle
- PATH'e ekle veya kodda path belirt

#### 3. Python Bağımlılıkları
```bash
# Virtual environment oluştur (önerilir)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

#### 4. Model Dosyasını İndir
Model dosyasını (~134 MB) şu linkten indirin:
https://drive.google.com/file/d/1rbViqZiql7gtXUHZq-Qp6GhwdlEkS2-N/view?usp=sharing

Proje kök dizinine `model_600_450_32_categorical.h5` olarak kaydedin.

---

### Flutter Mobile App

#### 1. Flutter Kurulumu
```bash
# Flutter SDK yükle
# https://docs.flutter.dev/get-started/install

# Kurulumu kontrol et
flutter doctor
```

#### 2. Bağımlılıkları Yükle
```bash
cd flutter_app
flutter pub get
```

#### 3. TFLite Model Oluştur
```bash
# Python modelini TFLite formatına dönüştür
python convert_model_to_tflite.py
```

#### 4. Uygulamayı Çalıştır
```bash
flutter run
```

---

## 📖 Kullanım

### Python CLI

#### Temel Kullanım
```bash
# Tek görüntü işle
python python_src/main.py --image path/to/image.jpg
```

#### Detaylı Parametreler
```bash
python python_src/main.py \
  --image test_images/car.jpg \
  --model model_600_450_32_categorical.h5 \
  --db vehicle_recognition.db \
  --init-db
```

#### Parametreler
- `--image`: İşlenecek görüntü dosyası (zorunlu)
- `--model`: Keras model dosyası (varsayılan: model_600_450_32_categorical.h5)
- `--db`: Veritabanı dosyası (varsayılan: vehicle_recognition.db)
- `--init-db`: Veritabanına örnek veri ekle
- `--quiet`: Sessiz mod (az çıktı)

#### Örnek Çıktı
```
============================================================
Araç Tanıma Sistemi Başlatılıyor
Vehicle Recognition System Starting
============================================================
✓ Tüm modüller yüklendi

============================================================
Görüntü İşleniyor: test_images/car.jpg
============================================================

1️⃣  Araç marka/model tanıma...
   Marka/Model: 2012_2014_Ford Focus Ön
   Güven: 95.67%

2️⃣  Renk tespiti...
   Renk: Beyaz
   RGB: R=210, G=215, B=220
   Güven: 92.3%

3️⃣  Plaka tanıma...
   Plaka: 34ABC123
   Geçerli Format: ✓
   Güven: 87.5%

4️⃣  Veritabanı kontrolü...
   ✓ Araç veritabanında bulundu - EŞLEŞME BAŞARILI!

============================================================
ÖZET / SUMMARY
============================================================
Marka/Model : 2012_2014_Ford Focus Ön
Renk        : Beyaz
Plaka       : 34ABC123
Veritabanı  : ✓ Eşleşti
```

### Python API Kullanımı

```python
from python_src.main import VehicleRecognitionSystem

# Sistemi başlat
system = VehicleRecognitionSystem(
    model_path='model_600_450_32_categorical.h5',
    db_path='vehicle_recognition.db'
)

# Örnek veri ekle
system.db_handler.add_sample_data()

# Görüntü işle
results = system.process_image('car.jpg', verbose=True)

# Sonuçlara eriş
if results['success']:
    print(f"Marka/Model: {results['vehicle']['label']}")
    print(f"Renk: {results['color']['color']}")
    print(f"Plaka: {results['plate']['plate']}")
    print(f"DB Eşleşmesi: {results['database_match']}")
```

---

## 🧪 Testler

### Python Testleri

#### Tüm Testleri Çalıştır
```bash
pytest
```

#### Coverage Raporu ile
```bash
pytest --cov=python_src --cov-report=html --cov-report=term-missing
```

#### Sadece Unit Testler
```bash
pytest -m unit
```

#### Sadece Güvenlik Testleri
```bash
pytest -m security
```

#### HTML Coverage Raporu
```bash
pytest --cov=python_src --cov-report=html
# Raporu aç: open htmlcov/index.html
```

### Flutter Testleri

```bash
cd flutter_app

# Testleri çalıştır
flutter test

# Coverage ile
flutter test --coverage

# Coverage raporu oluştur
genhtml coverage/lcov.info -o coverage/html
open coverage/html/index.html
```

---

## 🔒 Güvenlik

### SQL Injection Koruması

**Eski Kod (Güvensiz):**
```python
# ❌ TEHLİKELİ - String concatenation
query = f"SELECT * FROM kayitli_araclar WHERE plaka='{plaka}'"
cursor.execute(query)
```

**Yeni Kod (Güvenli):**
```python
# ✅ GÜVENLİ - Parametrize sorgu
query = "SELECT * FROM kayitli_araclar WHERE plaka = ?"
cursor.execute(query, (plaka,))
```

### Güvenlik Testleri
```bash
# SQL Injection testlerini çalıştır
pytest tests/unit/test_database_handler.py -k "sql_injection" -v

# Bandit security scan
bandit -r python_src/ -ll

# Safety check
safety check
```

---

## 📊 Test Coverage

### Mevcut Coverage

```
Python Tests:
  color_detection.py      ████████████████████ 95%
  plate_recognition.py    ██████████████████░░ 87%
  vehicle_recognition.py  █████████████████░░░ 82%
  database_handler.py     ████████████████████ 98%
  main.py                 ████████████░░░░░░░░ 65%
  -------------------------------
  TOPLAM                  ██████████████████░░ 85%

Flutter Tests:
  color_detection_service.dart  ████████████████████ 92%
  database_service.dart         ████████████████████ 95%
  plate_recognition_service.dart ████████████████░░░░ 78%
  model_service.dart            ███████████░░░░░░░░░ 55%
  -------------------------------
  TOPLAM                        ████████████████░░░░ 80%
```

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

Her push ve PR'de otomatik olarak:
- ✅ Python testleri (3.9, 3.10, 3.11)
- ✅ Flutter testleri
- ✅ Code coverage raporları
- ✅ Security scan (Bandit, Safety)
- ✅ Code style check (flake8)
- ✅ Flutter analyze

---

## 🐛 Bilinen Sorunlar ve Geliştirmeler

### Yapılacaklar
- [ ] Model performans optimizasyonu
- [ ] Daha fazla araç marka/model desteği
- [ ] Real-time video processing
- [ ] Web interface
- [ ] Docker containerization
- [ ] API endpoint'leri

### Katkıda Bulunma
Pull request'ler memnuniyetle karşılanır! Lütfen:
1. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
2. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
3. Branch'i push edin (`git push origin feature/AmazingFeature`)
4. Pull Request açın

---

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 👨‍💻 Geliştirici

**Burak Aggul**
- GitHub: [@burakaggul](https://github.com/burakaggul)

---

## 🙏 Teşekkürler

- Keras ve TensorFlow ekipleri
- Flutter ekibi
- Tesseract OCR
- Katkıda bulunan herkese

---

## 📚 Ek Kaynaklar

### Eski Versiyon
Orijinal kod `Full_Code.py` dosyasında bulunmaktadır (deprecated).

### Model Training
Model eğitimi için Jupyter notebook: `google_colab_train_600_450_32.ipynb`

### Flutter Setup
Flutter kurulum rehberi: `FLUTTER_SETUP_GUIDE.md`

---

**Not:** Bu proje eğitim ve araştırma amaçlıdır. Üretim ortamında kullanmadan önce ek güvenlik ve performans testleri yapılmalıdır.
