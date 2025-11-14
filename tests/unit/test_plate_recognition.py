"""
Plate Recognition Module Unit Tests
Plaka Tanıma Modülü Birim Testleri
"""

import pytest
from plate_recognition import PlateRecognizer


class TestPlateRecognizer:
    """PlateRecognizer sınıfı için test suite"""

    def test_init(self):
        """PlateRecognizer başlatma testi"""
        recognizer = PlateRecognizer()
        assert recognizer is not None

    @pytest.mark.unit
    def test_clean_plate_text(self):
        """Plaka metni temizleme testi"""
        recognizer = PlateRecognizer()

        # Özel karakterlerle
        dirty = "34 ABC 123"
        cleaned = recognizer._clean_plate_text(dirty)
        assert cleaned == "34ABC123"

    @pytest.mark.unit
    def test_clean_plate_text_with_special_chars(self):
        """Özel karakterlerle plaka temizleme testi"""
        recognizer = PlateRecognizer()

        dirty = "34-ABC-123!?"
        cleaned = recognizer._clean_plate_text(dirty)
        assert cleaned == "34ABC123"

    @pytest.mark.unit
    def test_clean_plate_text_lowercase(self):
        """Küçük harflerle plaka temizleme testi"""
        recognizer = PlateRecognizer()

        dirty = "34abc123"
        cleaned = recognizer._clean_plate_text(dirty)
        assert cleaned == "34ABC123"

    @pytest.mark.unit
    def test_clean_plate_text_empty(self):
        """Boş metin temizleme testi"""
        recognizer = PlateRecognizer()

        cleaned = recognizer._clean_plate_text("")
        assert cleaned is None

    @pytest.mark.unit
    def test_clean_plate_text_only_special_chars(self):
        """Sadece özel karakterler testi"""
        recognizer = PlateRecognizer()

        cleaned = recognizer._clean_plate_text("!@#$%^&*()")
        assert cleaned is None

    @pytest.mark.unit
    def test_is_valid_turkish_plate_valid(self):
        """Geçerli Türk plakası format testi"""
        recognizer = PlateRecognizer()

        # Geçerli formatlar
        assert recognizer._is_valid_turkish_plate("34ABC123") is True
        assert recognizer._is_valid_turkish_plate("06XYZ9999") is True
        assert recognizer._is_valid_turkish_plate("01A1234") is True
        assert recognizer._is_valid_turkish_plate("34AB1234") is True

    @pytest.mark.unit
    def test_is_valid_turkish_plate_invalid(self):
        """Geçersiz plaka format testi"""
        recognizer = PlateRecognizer()

        # Geçersiz formatlar
        assert recognizer._is_valid_turkish_plate("ABC123") is False  # Rakam ile başlamalı
        assert recognizer._is_valid_turkish_plate("34ABCD123") is False  # 3 harften fazla
        assert recognizer._is_valid_turkish_plate("341234") is False  # Harf yok
        assert recognizer._is_valid_turkish_plate("34A12345") is False  # 4 rakamdan fazla
        assert recognizer._is_valid_turkish_plate("3ABC123") is False  # 2 rakam ile başlamalı

    @pytest.mark.unit
    def test_calculate_confidence_valid_plate(self):
        """Geçerli plaka için güven skoru testi"""
        recognizer = PlateRecognizer()

        confidence = recognizer._calculate_confidence("34ABC123")

        assert confidence > 0.5  # Geçerli format için yüksek güven
        assert confidence <= 1.0

    @pytest.mark.unit
    def test_calculate_confidence_invalid_plate(self):
        """Geçersiz plaka için güven skoru testi"""
        recognizer = PlateRecognizer()

        confidence = recognizer._calculate_confidence("INVALID")

        assert confidence < 0.5  # Geçersiz format için düşük güven

    @pytest.mark.unit
    def test_calculate_confidence_short_plate(self):
        """Kısa plaka için güven skoru testi"""
        recognizer = PlateRecognizer()

        confidence = recognizer._calculate_confidence("34A12")

        assert confidence < 0.5  # Kısa plaka için düşük güven

    @pytest.mark.unit
    def test_calculate_confidence_long_plate(self):
        """Uzun plaka için güven skoru testi"""
        recognizer = PlateRecognizer()

        confidence = recognizer._calculate_confidence("34ABCDE12345")

        assert confidence < 0.5  # Çok uzun plaka için düşük güven

    @pytest.mark.unit
    def test_recognize_plate_file_not_found(self):
        """Dosya bulunamadı testi"""
        recognizer = PlateRecognizer()

        result = recognizer.recognize_plate("nonexistent_image.jpg")

        assert result is None

    @pytest.mark.unit
    def test_edge_cases_clean_plate(self):
        """Kenar durumları - plaka temizleme"""
        recognizer = PlateRecognizer()

        # Tab ve newline karakterleri
        assert recognizer._clean_plate_text("34\tABC\n123") == "34ABC123"

        # Birden fazla boşluk
        assert recognizer._clean_plate_text("34   ABC   123") == "34ABC123"

        # Mixed case
        assert recognizer._clean_plate_text("34AbC123") == "34ABC123"

    @pytest.mark.unit
    def test_recognize_plate_advanced_structure(self, sample_image):
        """Gelişmiş plaka tanıma yapısı testi"""
        recognizer = PlateRecognizer()

        result = recognizer.recognize_plate_advanced(sample_image)

        # Sonuç yapısını kontrol et
        assert 'plate' in result
        assert 'detected' in result
        assert 'confidence' in result
        assert 'raw_text' in result
        assert 'is_valid_format' in result

    @pytest.mark.unit
    def test_confidence_score_ranges(self):
        """Güven skoru aralıkları testi"""
        recognizer = PlateRecognizer()

        # Farklı plakalar için güven skorları
        plates = [
            ("34ABC123", 0.7, 1.0),  # İdeal format
            ("34A1234", 0.7, 1.0),   # İdeal format
            ("INVALID", 0.0, 0.5),   # Geçersiz
            ("34AB", 0.0, 0.5),      # Çok kısa
        ]

        for plate, min_conf, max_conf in plates:
            conf = recognizer._calculate_confidence(plate)
            assert min_conf <= conf <= max_conf, f"Plaka {plate} için güven skoru beklenenden farklı: {conf}"

    @pytest.mark.unit
    def test_turkish_plate_formats(self):
        """Çeşitli Türk plaka formatları testi"""
        recognizer = PlateRecognizer()

        # Farklı il kodları ve formatlar
        valid_plates = [
            "01A1",      # Minimum
            "01A1234",   # 1 harf 4 rakam
            "01AB123",   # 2 harf 3 rakam
            "01ABC1",    # 3 harf 1 rakam
            "01ABC1234", # 3 harf 4 rakam (maksimum)
            "34ABC123",  # İstanbul
            "06XYZ456",  # Ankara
            "35TEST99",  # İzmir
        ]

        for plate in valid_plates:
            assert recognizer._is_valid_turkish_plate(plate), f"Geçerli plaka geçersiz sayıldı: {plate}"

    @pytest.mark.unit
    def test_invalid_plate_patterns(self):
        """Geçersiz plaka desenleri testi"""
        recognizer = PlateRecognizer()

        invalid_plates = [
            "1ABC123",    # 1 rakam ile başlıyor
            "ABC12345",   # Rakam ile başlamıyor
            "34ABCD123",  # 4 harf
            "34ABC12345", # 5 rakam
            "341234567",  # Harf yok
            "34",         # Çok kısa
            "",           # Boş
        ]

        for plate in invalid_plates:
            assert not recognizer._is_valid_turkish_plate(plate), f"Geçersiz plaka geçerli sayıldı: {plate}"
