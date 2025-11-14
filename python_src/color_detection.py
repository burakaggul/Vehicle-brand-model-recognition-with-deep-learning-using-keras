#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Araç Rengi Tespit Modülü
Vehicle Color Detection Module
"""

import cv2
import numpy as np
from typing import Tuple, Dict


class ColorDetector:
    """Araç rengini tespit eden sınıf"""

    # Renk sınıflandırma eşikleri (RGB formatında - OpenCV BGR'den dönüştürülmüş)
    COLOR_RANGES = {
        'Beyaz': {
            'r_min': 170, 'r_max': 255,
            'g_min': 180, 'g_max': 255,
            'b_min': 180, 'b_max': 255
        },
        'Füme': {
            'r_min': 110, 'r_max': 150,
            'g_min': 110, 'g_max': 150,
            'b_min': 110, 'b_max': 150
        },
        'Gri': {
            'r_min': 150, 'r_max': 170,
            'g_min': 150, 'g_max': 180,
            'b_min': 150, 'b_max': 180
        },
        'Lacivert': {
            'r_min': 0, 'r_max': 150,
            'g_min': 25, 'g_max': 150,
            'b_min': 130, 'b_max': 255
        },
        'Kırmızı': {
            'r_min': 100, 'r_max': 255,
            'g_min': 0, 'g_max': 150,
            'b_min': 0, 'b_max': 150
        },
        'Siyah': {
            'r_min': 0, 'r_max': 110,
            'g_min': 0, 'g_max': 110,
            'b_min': 0, 'b_max': 110
        }
    }

    def __init__(self, target_width: int = 600, target_height: int = 450):
        """
        ColorDetector sınıfını başlatır

        Args:
            target_width: Hedef görüntü genişliği
            target_height: Hedef görüntü yüksekliği
        """
        self.target_width = target_width
        self.target_height = target_height

    def detect_color(self, image_path: str) -> str:
        """
        Görüntüden araç rengini tespit eder

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Tespit edilen renk adı (Türkçe)

        Raises:
            FileNotFoundError: Görüntü bulunamazsa
            ValueError: Geçersiz görüntü formatı
        """
        # Görüntüyü yükle
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if image is None:
            raise FileNotFoundError(f"Görüntü bulunamadı: {image_path}")

        # RGB değerlerini al
        avg_rgb = self._get_average_rgb(image)

        # Rengi sınıflandır
        color = self._classify_color(avg_rgb['r'], avg_rgb['g'], avg_rgb['b'])

        return color

    def _get_average_rgb(self, image: np.ndarray) -> Dict[str, int]:
        """
        Görüntünün belirli bölgelerinden ortalama RGB değerlerini hesaplar

        Args:
            image: OpenCV görüntü (BGR formatında)

        Returns:
            Ortalama RGB değerleri içeren dict
        """
        # Görüntüyü yeniden boyutlandır
        resized = cv2.resize(image, (self.target_width, self.target_height))

        # İki bölgeden renk örneği al (orijinal koddaki gibi)
        # Bölge 1: [y: 100:250, x: 100:350]
        crop_1 = resized[100:250, 100:350]

        # Bölge 2: [y: 100:250, x: 350:600]
        crop_2 = resized[100:250, 350:600]

        # Her bölgenin ortasından örnek al
        b_1, g_1, r_1 = self._get_center_pixel_bgr(crop_1)
        b_2, g_2, r_2 = self._get_center_pixel_bgr(crop_2)

        # Ortalamaları hesapla
        avg_r = int((r_1 + r_2) / 2)
        avg_g = int((g_1 + g_2) / 2)
        avg_b = int((b_1 + b_2) / 2)

        return {'r': avg_r, 'g': avg_g, 'b': avg_b}

    def _get_center_pixel_bgr(self, crop: np.ndarray) -> Tuple[int, int, int]:
        """
        Kesilmiş görüntünün merkez pikselinin BGR değerlerini döndürür

        Args:
            crop: Kesilmiş görüntü

        Returns:
            (b, g, r) tuple
        """
        height, width = crop.shape[:2]
        center_y, center_x = height // 2, width // 2

        pixel = crop[center_y, center_x]
        b, g, r = int(pixel[0]), int(pixel[1]), int(pixel[2])

        return b, g, r

    def _classify_color(self, r: int, g: int, b: int) -> str:
        """
        RGB değerlerine göre renk sınıflandırması yapar

        Args:
            r: Kırmızı kanal değeri (0-255)
            g: Yeşil kanal değeri (0-255)
            b: Mavi kanal değeri (0-255)

        Returns:
            Renk adı (Türkçe)
        """
        # Beyaz
        if (b >= 180 and b < 255 and
            g >= 180 and g < 255 and
            r >= 170 and r < 255):
            return "Beyaz"

        # Füme
        elif (b > 110 and b < 150 and
              g > 110 and g < 150 and
              r > 110 and r < 150):
            return "Füme"

        # Gri
        elif (b > 150 and b < 180 and
              g > 150 and g < 180 and
              r > 150 and r < 170):
            return "Gri"

        # Lacivert
        elif (b > 130 and b < 255 and
              g > 25 and g < 150 and
              r > 0 and r < 150):
            return "Lacivert"

        # Kırmızı
        elif (b > 0 and b < 150 and
              g > 0 and g < 150 and
              r > 100 and r < 255):
            return "Kırmızı"

        # Siyah
        elif (b <= 110 and g < 110 and r < 110):
            return "Siyah"

        # Varsayılan
        else:
            return "Diğer"

    def get_color_info(self, image_path: str) -> Dict:
        """
        Renk tespiti ve detaylı bilgi döndürür

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Renk bilgisi ve RGB değerleri içeren dict
        """
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if image is None:
            raise FileNotFoundError(f"Görüntü bulunamadı: {image_path}")

        avg_rgb = self._get_average_rgb(image)
        color = self._classify_color(avg_rgb['r'], avg_rgb['g'], avg_rgb['b'])

        return {
            'color': color,
            'rgb': avg_rgb,
            'confidence': self._calculate_confidence(avg_rgb, color)
        }

    def _calculate_confidence(self, rgb: Dict[str, int], color: str) -> float:
        """
        Renk sınıflandırmasının güven skorunu hesaplar

        Args:
            rgb: RGB değerleri
            color: Tespit edilen renk

        Returns:
            Güven skoru (0.0 - 1.0)
        """
        if color == "Diğer":
            return 0.5

        if color not in self.COLOR_RANGES:
            return 0.0

        ranges = self.COLOR_RANGES[color]

        # Her kanal için normalize edilmiş mesafeyi hesapla
        r_mid = (ranges['r_min'] + ranges['r_max']) / 2
        g_mid = (ranges['g_min'] + ranges['g_max']) / 2
        b_mid = (ranges['b_min'] + ranges['b_max']) / 2

        r_range = ranges['r_max'] - ranges['r_min']
        g_range = ranges['g_max'] - ranges['g_min']
        b_range = ranges['b_max'] - ranges['b_min']

        r_score = 1.0 - min(abs(rgb['r'] - r_mid) / (r_range / 2), 1.0) if r_range > 0 else 1.0
        g_score = 1.0 - min(abs(rgb['g'] - g_mid) / (g_range / 2), 1.0) if g_range > 0 else 1.0
        b_score = 1.0 - min(abs(rgb['b'] - b_mid) / (b_range / 2), 1.0) if b_range > 0 else 1.0

        # Ortalama güven skoru
        confidence = (r_score + g_score + b_score) / 3.0

        return round(confidence, 2)
