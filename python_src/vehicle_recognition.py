#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Araç Marka/Model Tanıma Modülü
Vehicle Brand/Model Recognition Module
"""

import numpy as np
from keras.models import load_model
from keras.preprocessing import image
from typing import Dict, List, Tuple
import os


class VehicleRecognizer:
    """Keras model ile araç marka/model tanıma sınıfı"""

    # Marka/Model etiketleri
    LABELS = [
        "2012_2014_Ford Focus Ön",
        "2012_2014_Ford Focus Arka",
        "2016_2019_Honda Civic Ön",
        "2016_2019_Honda Civic Arka"
    ]

    def __init__(self, model_path: str, target_size: Tuple[int, int] = (600, 450)):
        """
        VehicleRecognizer sınıfını başlatır

        Args:
            model_path: Keras model (.h5) dosya yolu
            target_size: Hedef görüntü boyutu (height, width)
        """
        self.model_path = model_path
        self.target_size = target_size
        self.model = None
        self._load_model()

    def _load_model(self):
        """Keras modelini yükler"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model dosyası bulunamadı: {self.model_path}")

        try:
            self.model = load_model(self.model_path)
            print(f"✓ Model yüklendi: {self.model_path}")
        except Exception as e:
            raise RuntimeError(f"Model yükleme hatası: {e}")

    def predict(self, image_path: str) -> Dict:
        """
        Görüntüden araç marka/model tahmini yapar

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Tahmin sonuçları dict
        """
        if self.model is None:
            raise RuntimeError("Model yüklenmedi!")

        # Görüntüyü yükle ve ön işle
        img_array = self._preprocess_image(image_path)

        # Tahmin yap
        predictions = self.model.predict(img_array, verbose=0)

        # Sonuçları işle
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        confidence = predictions[0][predicted_class_index]

        result = {
            'label': self.LABELS[predicted_class_index],
            'class_index': int(predicted_class_index),
            'confidence': float(confidence),
            'all_predictions': self._format_all_predictions(predictions[0])
        }

        return result

    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Görüntüyü model için ön işler

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Ön işlenmiş görüntü array
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Görüntü bulunamadı: {image_path}")

        # Görüntüyü yükle (target_size formatında)
        img = image.load_img(image_path, target_size=self.target_size)

        # Array'e dönüştür
        img_array = image.img_to_array(img)

        # Batch dimension ekle
        img_array = np.expand_dims(img_array, axis=0)

        # Not: VGG16 preprocess_input kullanılabilir ama
        # orijinal kodda kullanılmamış, bu yüzden eklenmedi

        return img_array

    def _format_all_predictions(self, predictions: np.ndarray) -> List[Dict]:
        """
        Tüm tahminleri formatlar

        Args:
            predictions: Tahmin array'i

        Returns:
            Formatlanmış tahminler listesi
        """
        results = []

        for i, prob in enumerate(predictions):
            results.append({
                'label': self.LABELS[i],
                'class_index': i,
                'probability': float(prob)
            })

        # Olasılığa göre sırala (yüksekten düşüğe)
        results.sort(key=lambda x: x['probability'], reverse=True)

        return results

    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """
        Birden fazla görüntü için toplu tahmin yapar

        Args:
            image_paths: Görüntü dosya yolları listesi

        Returns:
            Tahmin sonuçları listesi
        """
        results = []

        for img_path in image_paths:
            try:
                result = self.predict(img_path)
                results.append({
                    'image_path': img_path,
                    'success': True,
                    'prediction': result
                })
            except Exception as e:
                results.append({
                    'image_path': img_path,
                    'success': False,
                    'error': str(e)
                })

        return results

    def get_model_info(self) -> Dict:
        """
        Model bilgilerini döndürür

        Returns:
            Model bilgileri dict
        """
        if self.model is None:
            return {'loaded': False}

        return {
            'loaded': True,
            'model_path': self.model_path,
            'input_shape': self.model.input_shape,
            'output_shape': self.model.output_shape,
            'num_classes': len(self.LABELS),
            'labels': self.LABELS,
            'total_params': self.model.count_params()
        }
