#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plaka Tanıma Modülü
License Plate Recognition Module
"""

import cv2
import numpy as np
import imutils
import pytesseract
import re
from typing import Optional, Tuple, Dict


class PlateRecognizer:
    """Araç plakası tespit ve okuma sınıfı"""

    def __init__(self):
        """PlateRecognizer sınıfını başlatır"""
        # Pytesseract yapılandırması (Windows için path ayarlanabilir)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass

    def recognize_plate(self, image_path: str) -> Optional[str]:
        """
        Görüntüden plaka okur

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Temizlenmiş plaka metni veya None
        """
        try:
            # Plaka bölgesini tespit et
            plate_image = self._detect_plate_region(image_path)

            if plate_image is None:
                print("⚠ Plaka bölgesi tespit edilemedi")
                return None

            # OCR ile plaka metnini oku
            plate_text = self._extract_text_from_plate(plate_image)

            # Metni temizle
            cleaned_plate = self._clean_plate_text(plate_text)

            return cleaned_plate if cleaned_plate else None

        except Exception as e:
            print(f"❌ Plaka tanıma hatası: {e}")
            return None

    def _detect_plate_region(self, image_path: str) -> Optional[np.ndarray]:
        """
        Görüntüden plaka bölgesini tespit eder

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Kesilmiş plaka görüntüsü veya None
        """
        # Görüntüyü yükle
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if img is None:
            raise FileNotFoundError(f"Görüntü bulunamadı: {image_path}")

        # Gri tonlamaya çevir
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Bilateral filter ile gürültü azaltma
        gray = cv2.bilateralFilter(gray, 11, 17, 17)

        # Kenar tespiti
        edged = cv2.Canny(gray, 30, 200)

        # Konturları bul
        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

        # Plaka konturunu bul (4 köşeli)
        screen_cnt = None
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                screen_cnt = approx
                break

        if screen_cnt is None:
            return None

        # Plaka bölgesini kes
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [screen_cnt], 0, 255, -1)

        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))

        cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

        return cropped

    def _extract_text_from_plate(self, plate_image: np.ndarray) -> str:
        """
        Plaka görüntüsünden metni çıkarır (OCR)

        Args:
            plate_image: Plaka görüntüsü (gri tonlama)

        Returns:
            OCR ile okunan metin
        """
        # Pytesseract ile OCR
        # --psm 11: Sparse text mode
        text = pytesseract.image_to_string(plate_image, config='--psm 11')

        return text

    def _clean_plate_text(self, text: str) -> Optional[str]:
        """
        Plaka metnini temizler ve formatlar

        Args:
            text: Ham OCR metni

        Returns:
            Temizlenmiş plaka metni veya None
        """
        # Tüm özel karakterleri kaldır (orijinal regex)
        # re.sub('\ |\?|\.|\!|\/|\\|\;|\:|\'|\(|\)|\-|\{|\}|\]|\[|\&|\,|\'|\||\»|\¢|\*|\§|\°|','',t_plaka)
        pattern = r'[ \?\.\!\/\\\;\:\'\(\)\-\{\}\]\[\&\,\|\»\¢\*\§\°]'
        cleaned = re.sub(pattern, '', text)

        # Sadece alfanumerik karakterler
        cleaned = re.sub(r'[^A-Z0-9]', '', cleaned.upper())

        # Boş ise None döndür
        if not cleaned:
            return None

        return cleaned

    def recognize_plate_advanced(self, image_path: str) -> Dict:
        """
        Gelişmiş plaka tanıma - detaylı bilgi döndürür

        Args:
            image_path: Görüntü dosya yolu

        Returns:
            Plaka bilgileri dict
        """
        result = {
            'plate': None,
            'detected': False,
            'confidence': 0.0,
            'raw_text': None,
            'is_valid_format': False
        }

        try:
            # Plaka bölgesini tespit et
            plate_image = self._detect_plate_region(image_path)

            if plate_image is None:
                return result

            result['detected'] = True

            # OCR ile metni oku
            raw_text = self._extract_text_from_plate(plate_image)
            result['raw_text'] = raw_text

            # Temizle
            cleaned = self._clean_plate_text(raw_text)
            result['plate'] = cleaned

            # Türk plaka formatını kontrol et
            if cleaned:
                result['is_valid_format'] = self._is_valid_turkish_plate(cleaned)
                result['confidence'] = self._calculate_confidence(cleaned)

        except Exception as e:
            print(f"❌ Gelişmiş plaka tanıma hatası: {e}")

        return result

    def _is_valid_turkish_plate(self, plate: str) -> bool:
        """
        Türk plaka formatını kontrol eder

        Args:
            plate: Plaka metni

        Returns:
            True: Geçerli format
            False: Geçersiz format
        """
        # Türk plaka formatı: 2 rakam + 1-3 harf + 1-4 rakam
        # Örnek: 34ABC123, 06XYZ9999
        pattern = r'^[0-9]{2}[A-Z]{1,3}[0-9]{1,4}$'

        return bool(re.match(pattern, plate))

    def _calculate_confidence(self, plate: str) -> float:
        """
        Plaka tanıma güven skorunu hesaplar

        Args:
            plate: Temizlenmiş plaka metni

        Returns:
            Güven skoru (0.0 - 1.0)
        """
        score = 0.0

        # Uzunluk kontrolü (7-10 karakter ideal)
        if 7 <= len(plate) <= 10:
            score += 0.3

        # Türk plaka formatı kontrolü
        if self._is_valid_turkish_plate(plate):
            score += 0.5

        # Rakam ve harf dengesi
        letter_count = len(re.findall(r'[A-Z]', plate))
        digit_count = len(re.findall(r'[0-9]', plate))

        if 1 <= letter_count <= 3 and 3 <= digit_count <= 6:
            score += 0.2

        return min(score, 1.0)

    def visualize_detection(self, image_path: str, output_path: str):
        """
        Plaka tespitini görselleştirir ve kaydeder

        Args:
            image_path: Giriş görüntüsü
            output_path: Çıkış görüntüsü yolu
        """
        img = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if img is None:
            raise FileNotFoundError(f"Görüntü bulunamadı: {image_path}")

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bilateralFilter(gray, 11, 17, 17)
        edged = cv2.Canny(gray, 30, 200)

        cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

        screen_cnt = None
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                screen_cnt = approx
                break

        if screen_cnt is not None:
            # Plaka bölgesini çiz
            cv2.drawContours(img, [screen_cnt], -1, (0, 255, 0), 3)

        # Kaydet
        cv2.imwrite(output_path, img)
        print(f"✓ Görselleştirme kaydedildi: {output_path}")
