#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Dönüştürme Scripti: Keras .h5 -> TensorFlow Lite .tflite
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np

def convert_h5_to_tflite(h5_model_path, tflite_output_path):
    """
    Keras .h5 modelini TensorFlow Lite formatına dönüştürür

    Args:
        h5_model_path: .h5 model dosyasının yolu
        tflite_output_path: Çıktı .tflite dosyasının yolu
    """

    print(f"Model yükleniyor: {h5_model_path}")

    # Keras modelini yükle
    model = keras.models.load_model(h5_model_path)

    print("Model özeti:")
    model.summary()

    # TensorFlow Lite converter oluştur
    converter = tf.lite.TFLiteConverter.from_keras_model(model)

    # Optimizasyon ayarları (opsiyonel - mobil için)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]

    # Float16 quantization (model boyutunu küçültür)
    converter.target_spec.supported_types = [tf.float16]

    # Modeli dönüştür
    print("Model TFLite formatına dönüştürülüyor...")
    tflite_model = converter.convert()

    # TFLite modelini kaydet
    with open(tflite_output_path, 'wb') as f:
        f.write(tflite_model)

    print(f"✓ Model başarıyla dönüştürüldü: {tflite_output_path}")
    print(f"  Model boyutu: {len(tflite_model) / 1024 / 1024:.2f} MB")

    # Model doğrulama
    verify_tflite_model(tflite_output_path, model)

def verify_tflite_model(tflite_path, original_model):
    """
    TFLite modelini doğrular ve test eder
    """
    print("\nModel doğrulanıyor...")

    # TFLite interpreter oluştur
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    # Input ve output detayları
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print("\nInput detayları:")
    print(f"  Shape: {input_details[0]['shape']}")
    print(f"  Type: {input_details[0]['dtype']}")

    print("\nOutput detayları:")
    print(f"  Shape: {output_details[0]['shape']}")
    print(f"  Type: {output_details[0]['dtype']}")

    # Test görüntüsü ile doğrulama
    test_image = np.random.rand(1, 600, 450, 3).astype(np.float32)

    # TFLite ile tahmin
    interpreter.set_tensor(input_details[0]['index'], test_image)
    interpreter.invoke()
    tflite_output = interpreter.get_tensor(output_details[0]['index'])

    # Orijinal model ile tahmin
    keras_output = original_model.predict(test_image, verbose=0)

    # Sonuçları karşılaştır
    diff = np.max(np.abs(tflite_output - keras_output))
    print(f"\nModel doğrulaması: Maximum difference = {diff:.6f}")

    if diff < 0.01:
        print("✓ Model doğrulaması başarılı!")
    else:
        print("⚠ Uyarı: Model çıktıları arasında fark var")

def create_labels_file(output_path):
    """
    Model için etiket dosyası oluşturur
    """
    labels = [
        "2012_2014_Ford Focus Ön",
        "2012_2014_Ford Focus Arka",
        "2016_2019_Honda Civic Ön",
        "2016_2019_Honda Civic Arka"
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        for label in labels:
            f.write(label + '\n')

    print(f"✓ Etiket dosyası oluşturuldu: {output_path}")

if __name__ == "__main__":
    # Model dosya yolları
    H5_MODEL_PATH = "model_600_450_32_categorical.h5"
    TFLITE_OUTPUT_PATH = "flutter_app/assets/models/model.tflite"
    LABELS_OUTPUT_PATH = "flutter_app/assets/models/labels.txt"

    print("=" * 60)
    print("Keras Model -> TensorFlow Lite Dönüştürücü")
    print("=" * 60)

    try:
        # Modeli dönüştür
        convert_h5_to_tflite(H5_MODEL_PATH, TFLITE_OUTPUT_PATH)

        # Etiket dosyasını oluştur
        create_labels_file(LABELS_OUTPUT_PATH)

        print("\n" + "=" * 60)
        print("✓ Tüm işlemler başarıyla tamamlandı!")
        print("=" * 60)
        print("\nSonraki adımlar:")
        print("1. Flutter projesini açın: cd flutter_app")
        print("2. Bağımlılıkları yükleyin: flutter pub get")
        print("3. Uygulamayı çalıştırın: flutter run")

    except Exception as e:
        print(f"\n❌ Hata oluştu: {str(e)}")
        import traceback
        traceback.print_exc()
