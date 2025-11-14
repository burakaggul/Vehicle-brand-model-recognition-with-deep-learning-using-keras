"""
Color Detection Module Unit Tests
Renk Tespit Modülü Birim Testleri
"""

import pytest
import numpy as np
import cv2
from pathlib import Path

from color_detection import ColorDetector


class TestColorDetector:
    """ColorDetector sınıfı için test suite"""

    def test_init(self):
        """ColorDetector başlatma testi"""
        detector = ColorDetector()
        assert detector.target_width == 600
        assert detector.target_height == 450

    def test_init_custom_size(self):
        """Özel boyutla başlatma testi"""
        detector = ColorDetector(target_width=800, target_height=600)
        assert detector.target_width == 800
        assert detector.target_height == 600

    @pytest.mark.unit
    def test_detect_white_color(self, white_car_image):
        """Beyaz renk tespiti testi"""
        detector = ColorDetector()
        color = detector.detect_color(white_car_image)
        assert color == "Beyaz"

    @pytest.mark.unit
    def test_detect_black_color(self, black_car_image):
        """Siyah renk tespiti testi"""
        detector = ColorDetector()
        color = detector.detect_color(black_car_image)
        assert color == "Siyah"

    @pytest.mark.unit
    def test_detect_red_color(self, red_car_image):
        """Kırmızı renk tespiti testi"""
        detector = ColorDetector()
        color = detector.detect_color(red_car_image)
        assert color == "Kırmızı"

    @pytest.mark.unit
    def test_classify_color_white(self):
        """Beyaz renk sınıflandırma testi"""
        detector = ColorDetector()

        # Beyaz RGB değerleri
        color = detector._classify_color(r=200, g=200, b=200)
        assert color == "Beyaz"

    @pytest.mark.unit
    def test_classify_color_black(self):
        """Siyah renk sınıflandırma testi"""
        detector = ColorDetector()

        # Siyah RGB değerleri
        color = detector._classify_color(r=50, g=50, b=50)
        assert color == "Siyah"

    @pytest.mark.unit
    def test_classify_color_red(self):
        """Kırmızı renk sınıflandırma testi"""
        detector = ColorDetector()

        # Kırmızı RGB değerleri
        color = detector._classify_color(r=180, g=50, b=50)
        assert color == "Kırmızı"

    @pytest.mark.unit
    def test_classify_color_fume(self):
        """Füme renk sınıflandırma testi"""
        detector = ColorDetector()

        # Füme RGB değerleri
        color = detector._classify_color(r=130, g=130, b=130)
        assert color == "Füme"

    @pytest.mark.unit
    def test_classify_color_gray(self):
        """Gri renk sınıflandırma testi"""
        detector = ColorDetector()

        # Gri RGB değerleri
        color = detector._classify_color(r=160, g=165, b=165)
        assert color == "Gri"

    @pytest.mark.unit
    def test_classify_color_navy_blue(self):
        """Lacivert renk sınıflandırma testi"""
        detector = ColorDetector()

        # Lacivert RGB değerleri
        color = detector._classify_color(r=50, g=80, b=180)
        assert color == "Lacivert"

    @pytest.mark.unit
    def test_classify_color_other(self):
        """Diğer (tanımlanamayan) renk testi"""
        detector = ColorDetector()

        # Hiçbir kategoriye uymayan RGB değerleri
        color = detector._classify_color(r=75, g=200, b=100)
        assert color == "Diğer"

    @pytest.mark.unit
    def test_boundary_values_white(self):
        """Beyaz renk sınır değer testleri"""
        detector = ColorDetector()

        # Alt sınır (hemen üstü)
        assert detector._classify_color(r=170, g=180, b=180) == "Beyaz"

        # Üst sınır (hemen altı)
        assert detector._classify_color(r=254, g=254, b=254) == "Beyaz"

    @pytest.mark.unit
    def test_boundary_values_black(self):
        """Siyah renk sınır değer testleri"""
        detector = ColorDetector()

        # Tam sınır
        assert detector._classify_color(r=110, g=109, b=110) == "Siyah"

        # Minimum
        assert detector._classify_color(r=0, g=0, b=0) == "Siyah"

    @pytest.mark.unit
    def test_get_color_info(self, white_car_image):
        """Detaylı renk bilgisi testi"""
        detector = ColorDetector()
        info = detector.get_color_info(white_car_image)

        assert 'color' in info
        assert 'rgb' in info
        assert 'confidence' in info
        assert info['color'] == "Beyaz"
        assert 0.0 <= info['confidence'] <= 1.0

    @pytest.mark.unit
    def test_confidence_calculation(self):
        """Güven skoru hesaplama testi"""
        detector = ColorDetector()

        # Tam ortada (maksimum güven)
        confidence = detector._calculate_confidence(
            rgb={'r': 200, 'g': 200, 'b': 200},
            color='Beyaz'
        )
        assert confidence > 0.5

        # "Diğer" kategorisi için orta güven
        confidence = detector._calculate_confidence(
            rgb={'r': 100, 'g': 100, 'b': 100},
            color='Diğer'
        )
        assert confidence == 0.5

    @pytest.mark.unit
    def test_file_not_found_error(self):
        """Dosya bulunamadı hatası testi"""
        detector = ColorDetector()

        with pytest.raises(FileNotFoundError):
            detector.detect_color('nonexistent_image.jpg')

    @pytest.mark.unit
    def test_get_average_rgb(self, white_car_image):
        """Ortalama RGB değerleri hesaplama testi"""
        detector = ColorDetector()

        # Görüntüyü yükle
        image = cv2.imread(white_car_image, cv2.IMREAD_COLOR)

        rgb = detector._get_average_rgb(image)

        assert 'r' in rgb
        assert 'g' in rgb
        assert 'b' in rgb
        assert 0 <= rgb['r'] <= 255
        assert 0 <= rgb['g'] <= 255
        assert 0 <= rgb['b'] <= 255

    @pytest.mark.unit
    def test_get_center_pixel_bgr(self):
        """Merkez piksel BGR testi"""
        detector = ColorDetector()

        # 100x100 kırmızı görüntü oluştur (BGR)
        crop = np.zeros((100, 100, 3), dtype=np.uint8)
        crop[:, :] = [0, 0, 255]  # BGR kırmızı

        b, g, r = detector._get_center_pixel_bgr(crop)

        assert b == 0
        assert g == 0
        assert r == 255

    @pytest.mark.unit
    def test_pure_colors(self):
        """Saf renkler testi"""
        detector = ColorDetector()

        # Saf beyaz
        assert detector._classify_color(255, 255, 255) == "Beyaz"

        # Saf siyah
        assert detector._classify_color(0, 0, 0) == "Siyah"

    @pytest.mark.unit
    def test_edge_cases(self):
        """Kenar durumları testi"""
        detector = ColorDetector()

        # Negatif değerler (olmamalı ama test edelim)
        # Not: Gerçek kodda bu durumlar RGB aralığında olmalı
        # Bu test kod savunmasını kontrol eder

        # Tam sınır değerleri
        assert detector._classify_color(110, 110, 110) == "Siyah"
        assert detector._classify_color(111, 111, 111) == "Füme"
