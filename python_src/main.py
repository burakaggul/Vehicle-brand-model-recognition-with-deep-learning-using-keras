#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Araç Tanıma Ana Modül
Vehicle Recognition Main Module - Refactored & Secure Version

Orijinal Full_Code.py'nin yeniden yazılmış, güvenli versiyonu
"""

import argparse
from pathlib import Path
from typing import Dict
import sys

from color_detection import ColorDetector
from plate_recognition import PlateRecognizer
from vehicle_recognition import VehicleRecognizer
from database_handler import DatabaseHandler


class VehicleRecognitionSystem:
    """Tam araç tanıma sistemi - tüm modülleri birleştirir"""

    def __init__(self, model_path: str, db_path: str = 'vehicle_recognition.db'):
        """
        Sistem başlatma

        Args:
            model_path: Keras model dosya yolu
            db_path: Veritabanı dosya yolu
        """
        print("=" * 60)
        print("Araç Tanıma Sistemi Başlatılıyor")
        print("Vehicle Recognition System Starting")
        print("=" * 60)

        # Modülleri başlat
        self.color_detector = ColorDetector()
        self.plate_recognizer = PlateRecognizer()
        self.vehicle_recognizer = VehicleRecognizer(model_path)
        self.db_handler = DatabaseHandler(db_path)

        print("✓ Tüm modüller yüklendi")

    def process_image(self, image_path: str, verbose: bool = True) -> Dict:
        """
        Tek bir görüntüyü işler - araç tanıma, renk tespiti, plaka okuma

        Args:
            image_path: Görüntü dosya yolu
            verbose: Detaylı çıktı göster

        Returns:
            Sonuçlar dict
        """
        if verbose:
            print(f"\n{'=' * 60}")
            print(f"Görüntü İşleniyor: {image_path}")
            print("=" * 60)

        results = {
            'image_path': image_path,
            'success': True,
            'vehicle': None,
            'color': None,
            'plate': None,
            'database_match': False,
            'errors': []
        }

        try:
            # 1. Araç Marka/Model Tanıma
            if verbose:
                print("\n1️⃣  Araç marka/model tanıma...")

            vehicle_result = self.vehicle_recognizer.predict(image_path)
            results['vehicle'] = vehicle_result

            if verbose:
                print(f"   Marka/Model: {vehicle_result['label']}")
                print(f"   Güven: {vehicle_result['confidence']:.2%}")

        except Exception as e:
            results['errors'].append(f"Araç tanıma hatası: {e}")
            if verbose:
                print(f"   ❌ Hata: {e}")

        try:
            # 2. Renk Tespiti
            if verbose:
                print("\n2️⃣  Renk tespiti...")

            color_result = self.color_detector.get_color_info(image_path)
            results['color'] = color_result

            if verbose:
                print(f"   Renk: {color_result['color']}")
                print(f"   RGB: R={color_result['rgb']['r']}, G={color_result['rgb']['g']}, B={color_result['rgb']['b']}")
                print(f"   Güven: {color_result['confidence']:.2%}")

        except Exception as e:
            results['errors'].append(f"Renk tespiti hatası: {e}")
            if verbose:
                print(f"   ❌ Hata: {e}")

        try:
            # 3. Plaka Tanıma
            if verbose:
                print("\n3️⃣  Plaka tanıma...")

            plate_result = self.plate_recognizer.recognize_plate_advanced(image_path)
            results['plate'] = plate_result

            if verbose:
                if plate_result['plate']:
                    print(f"   Plaka: {plate_result['plate']}")
                    print(f"   Geçerli Format: {'✓' if plate_result['is_valid_format'] else '✗'}")
                    print(f"   Güven: {plate_result['confidence']:.2%}")
                else:
                    print("   ⚠ Plaka tespit edilemedi")

        except Exception as e:
            results['errors'].append(f"Plaka tanıma hatası: {e}")
            if verbose:
                print(f"   ❌ Hata: {e}")

        # 4. Veritabanı Kontrolü
        if results['vehicle'] and results['color'] and results['plate']:
            if results['plate']['plate']:
                if verbose:
                    print("\n4️⃣  Veritabanı kontrolü...")

                try:
                    db_match = self.db_handler.check_vehicle(
                        marka_model=results['vehicle']['label'],
                        plaka=results['plate']['plate'],
                        renk=results['color']['color']
                    )

                    results['database_match'] = db_match

                    if verbose:
                        if db_match:
                            print("   ✓ Araç veritabanında bulundu - EŞLEŞME BAŞARILI!")
                        else:
                            print("   ✗ Araç veritabanında bulunamadı - EŞLEŞME BAŞARISIZ!")

                except Exception as e:
                    results['errors'].append(f"Veritabanı sorgu hatası: {e}")
                    if verbose:
                        print(f"   ❌ Hata: {e}")

        # Özet
        if verbose:
            print("\n" + "=" * 60)
            print("ÖZET / SUMMARY")
            print("=" * 60)
            if results['vehicle']:
                print(f"Marka/Model : {results['vehicle']['label']}")
            if results['color']:
                print(f"Renk        : {results['color']['color']}")
            if results['plate'] and results['plate']['plate']:
                print(f"Plaka       : {results['plate']['plate']}")
            print(f"Veritabanı  : {'✓ Eşleşti' if results['database_match'] else '✗ Eşleşmedi'}")

            if results['errors']:
                print("\nHatalar:")
                for error in results['errors']:
                    print(f"  - {error}")

        return results

    def add_vehicle_to_db(self, marka_model: str, plaka: str, renk: str) -> bool:
        """
        Veritabanına araç ekler

        Args:
            marka_model: Marka/model bilgisi
            plaka: Plaka
            renk: Renk

        Returns:
            Başarılı ise True
        """
        try:
            vehicle_id = self.db_handler.insert_vehicle(marka_model, plaka, renk)
            print(f"✓ Araç eklendi (ID: {vehicle_id})")
            return True
        except Exception as e:
            print(f"❌ Araç eklenemedi: {e}")
            return False


def main():
    """Ana program"""
    parser = argparse.ArgumentParser(description='Araç Tanıma Sistemi')

    parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='İşlenecek görüntü dosyası yolu'
    )

    parser.add_argument(
        '--model',
        type=str,
        default='model_600_450_32_categorical.h5',
        help='Keras model dosyası yolu (default: model_600_450_32_categorical.h5)'
    )

    parser.add_argument(
        '--db',
        type=str,
        default='vehicle_recognition.db',
        help='Veritabanı dosyası yolu (default: vehicle_recognition.db)'
    )

    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Veritabanına örnek veri ekle'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Sessiz mod (az çıktı)'
    )

    args = parser.parse_args()

    # Görüntü dosyası kontrolü
    if not Path(args.image).exists():
        print(f"❌ Hata: Görüntü bulunamadı: {args.image}")
        sys.exit(1)

    # Model dosyası kontrolü
    if not Path(args.model).exists():
        print(f"❌ Hata: Model dosyası bulunamadı: {args.model}")
        print("Model dosyasını buradan indirebilirsiniz:")
        print("https://drive.google.com/file/d/1rbViqZiql7gtXUHZq-Qp6GhwdlEkS2-N/view?usp=sharing")
        sys.exit(1)

    try:
        # Sistemi başlat
        system = VehicleRecognitionSystem(
            model_path=args.model,
            db_path=args.db
        )

        # Örnek veri ekle (istenirse)
        if args.init_db:
            print("\nÖrnek veri ekleniyor...")
            system.db_handler.add_sample_data()
            print("✓ Örnek veri eklendi")

        # Görüntüyü işle
        results = system.process_image(args.image, verbose=not args.quiet)

        # Çıkış kodu
        sys.exit(0 if results['success'] and results['database_match'] else 1)

    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
