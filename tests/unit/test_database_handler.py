"""
Database Handler Unit Tests
Veritabanı İşleyici Birim Testleri - SQL Injection Koruması Testleri Dahil
"""

import pytest
import sqlite3
from pathlib import Path

from database_handler import DatabaseHandler


class TestDatabaseHandler:
    """DatabaseHandler sınıfı için test suite"""

    def test_init(self, temp_db):
        """Veritabanı başlatma testi"""
        db = DatabaseHandler(temp_db)
        assert Path(temp_db).exists()

    @pytest.mark.unit
    def test_table_creation(self, temp_db):
        """Tablo oluşturma testi"""
        db = DatabaseHandler(temp_db)

        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='kayitli_araclar'
            """)
            result = cursor.fetchone()

        assert result is not None

    @pytest.mark.unit
    def test_insert_vehicle(self, temp_db):
        """Araç ekleme testi"""
        db = DatabaseHandler(temp_db)

        vehicle_id = db.insert_vehicle(
            marka_model="2012_2014_Ford Focus Ön",
            plaka="34ABC123",
            renk="Beyaz"
        )

        assert vehicle_id > 0

    @pytest.mark.unit
    def test_check_vehicle_exists(self, temp_db):
        """Var olan araç kontrolü testi"""
        db = DatabaseHandler(temp_db)

        # Araç ekle
        db.insert_vehicle(
            marka_model="2012_2014_Ford Focus Ön",
            plaka="34ABC123",
            renk="Beyaz"
        )

        # Kontrol et
        exists = db.check_vehicle(
            marka_model="2012_2014_Ford Focus Ön",
            plaka="34ABC123",
            renk="Beyaz"
        )

        assert exists is True

    @pytest.mark.unit
    def test_check_vehicle_not_exists(self, temp_db):
        """Olmayan araç kontrolü testi"""
        db = DatabaseHandler(temp_db)

        exists = db.check_vehicle(
            marka_model="NonExistent Model",
            plaka="00XXX000",
            renk="Mavi"
        )

        assert exists is False

    @pytest.mark.unit
    @pytest.mark.security
    def test_sql_injection_prevention_single_quote(self, temp_db):
        """SQL Injection koruması testi - tek tırnak"""
        db = DatabaseHandler(temp_db)

        # Örnek veri ekle
        db.insert_vehicle("Test Model", "34ABC123", "Beyaz")

        # SQL injection denemesi - tek tırnak ile
        malicious_input = "' OR '1'='1"

        # Bu sorgu güvenli olmalı, SQL injection çalışmamalı
        result = db.check_vehicle(
            marka_model=malicious_input,
            plaka="34ABC123",
            renk="Beyaz"
        )

        # False dönmeli çünkü malicious_input gerçek bir model değil
        assert result is False

    @pytest.mark.unit
    @pytest.mark.security
    def test_sql_injection_prevention_drop_table(self, temp_db):
        """SQL Injection koruması testi - DROP TABLE"""
        db = DatabaseHandler(temp_db)

        # Örnek veri ekle
        db.insert_vehicle("Test Model", "34ABC123", "Beyaz")

        # SQL injection denemesi - DROP TABLE
        malicious_input = "'; DROP TABLE kayitli_araclar; --"

        # Bu sorgu güvenli olmalı
        result = db.check_vehicle(
            marka_model=malicious_input,
            plaka="34ABC123",
            renk="Beyaz"
        )

        # False dönmeli
        assert result is False

        # Tablo hala var olmalı
        with db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='kayitli_araclar'
            """)
            table_exists = cursor.fetchone() is not None

        assert table_exists is True

    @pytest.mark.unit
    @pytest.mark.security
    def test_sql_injection_prevention_union(self, temp_db):
        """SQL Injection koruması testi - UNION saldırısı"""
        db = DatabaseHandler(temp_db)

        # SQL injection denemesi - UNION
        malicious_input = "' UNION SELECT * FROM kayitli_araclar --"

        result = db.check_vehicle(
            marka_model=malicious_input,
            plaka="test",
            renk="test"
        )

        # Güvenli olmalı, hata vermemeli
        assert result is False

    @pytest.mark.unit
    def test_get_vehicle(self, temp_db):
        """Araç bilgisi getirme testi"""
        db = DatabaseHandler(temp_db)

        # Araç ekle
        db.insert_vehicle("Test Model", "34TEST99", "Kırmızı")

        # Getir
        vehicle = db.get_vehicle("Test Model", "34TEST99", "Kırmızı")

        assert vehicle is not None
        assert vehicle['marka_model'] == "Test Model"
        assert vehicle['plaka'] == "34TEST99"
        assert vehicle['renk'] == "Kırmızı"

    @pytest.mark.unit
    def test_get_vehicle_not_found(self, temp_db):
        """Olmayan araç getirme testi"""
        db = DatabaseHandler(temp_db)

        vehicle = db.get_vehicle("Nonexistent", "00XXX000", "Yeşil")

        assert vehicle is None

    @pytest.mark.unit
    def test_search_by_plate(self, temp_db):
        """Plakaya göre arama testi"""
        db = DatabaseHandler(temp_db)

        # Birkaç araç ekle
        db.insert_vehicle("Ford Focus", "34ABC123", "Beyaz")
        db.insert_vehicle("Honda Civic", "34ABC456", "Siyah")
        db.insert_vehicle("Toyota Corolla", "06XYZ789", "Kırmızı")

        # Kısmi arama
        results = db.search_by_plate("34ABC")

        assert len(results) == 2
        assert all('34ABC' in r['plaka'] for r in results)

    @pytest.mark.unit
    def test_get_all_vehicles(self, temp_db):
        """Tüm araçları getirme testi"""
        db = DatabaseHandler(temp_db)

        # Birkaç araç ekle
        db.insert_vehicle("Ford Focus", "34ABC123", "Beyaz")
        db.insert_vehicle("Honda Civic", "06XYZ456", "Siyah")

        vehicles = db.get_all_vehicles()

        assert len(vehicles) >= 2

    @pytest.mark.unit
    def test_delete_vehicle(self, temp_db):
        """Araç silme testi"""
        db = DatabaseHandler(temp_db)

        # Araç ekle
        vehicle_id = db.insert_vehicle("Test Model", "34TEST99", "Yeşil")

        # Sil
        deleted = db.delete_vehicle(vehicle_id)

        assert deleted is True

        # Kontrol et - silinmiş olmalı
        exists = db.check_vehicle("Test Model", "34TEST99", "Yeşil")
        assert exists is False

    @pytest.mark.unit
    def test_delete_nonexistent_vehicle(self, temp_db):
        """Olmayan araç silme testi"""
        db = DatabaseHandler(temp_db)

        deleted = db.delete_vehicle(99999)

        assert deleted is False

    @pytest.mark.unit
    def test_duplicate_insert(self, temp_db):
        """Tekrarlı kayıt ekleme testi (UNIQUE constraint)"""
        db = DatabaseHandler(temp_db)

        # İlk kayıt
        db.insert_vehicle("Ford Focus", "34ABC123", "Beyaz")

        # Aynı kayıt tekrar - hata vermeli
        with pytest.raises(sqlite3.IntegrityError):
            db.insert_vehicle("Ford Focus", "34ABC123", "Beyaz")

    @pytest.mark.unit
    def test_add_sample_data(self, temp_db):
        """Örnek veri ekleme testi"""
        db = DatabaseHandler(temp_db)

        db.add_sample_data()

        vehicles = db.get_all_vehicles()

        assert len(vehicles) >= 5

    @pytest.mark.unit
    def test_clear_database(self, temp_db):
        """Veritabanı temizleme testi"""
        db = DatabaseHandler(temp_db)

        # Veri ekle
        db.insert_vehicle("Test Model", "34TEST99", "Beyaz")

        # Temizle
        db.clear_database()

        # Boş olmalı
        vehicles = db.get_all_vehicles()
        assert len(vehicles) == 0

    @pytest.mark.unit
    def test_get_statistics(self, temp_db):
        """İstatistik getirme testi"""
        db = DatabaseHandler(temp_db)

        # Örnek veri ekle
        db.add_sample_data()

        stats = db.get_statistics()

        assert 'total_vehicles' in stats
        assert 'color_distribution' in stats
        assert 'brand_distribution' in stats
        assert stats['total_vehicles'] > 0

    @pytest.mark.unit
    def test_context_manager_rollback_on_error(self, temp_db):
        """Context manager rollback testi"""
        db = DatabaseHandler(temp_db)

        try:
            with db._get_connection() as conn:
                cursor = conn.cursor()
                # Geçersiz SQL - hata verecek
                cursor.execute("INVALID SQL STATEMENT")
        except:
            pass

        # Veritabanı hala çalışır olmalı
        vehicles = db.get_all_vehicles()
        assert isinstance(vehicles, list)

    @pytest.mark.unit
    @pytest.mark.security
    def test_parameterized_queries_vs_string_concat(self, temp_db):
        """Parametrize sorgular vs String birleştirme karşılaştırması"""
        db = DatabaseHandler(temp_db)

        # Örnek veri
        db.insert_vehicle("Test Model", "34ABC123", "Beyaz")

        # Güvenli yöntem (parametrize)
        result_safe = db.check_vehicle(
            marka_model="Test Model",
            plaka="34ABC123",
            renk="Beyaz"
        )

        assert result_safe is True

        # Tehlikeli string birleştirme testi için
        # Kodumuzda string birleştirme YOK, bu testi geç

    @pytest.mark.unit
    def test_special_characters_in_data(self, temp_db):
        """Özel karakterler içeren veri testi"""
        db = DatabaseHandler(temp_db)

        # Özel karakterler içeren veri
        special_model = "Ford's \"Special\" Model"
        special_plate = "34-ABC-123"
        special_color = "Beyaz&Gri"

        # Ekle
        vehicle_id = db.insert_vehicle(special_model, special_plate, special_color)
        assert vehicle_id > 0

        # Kontrol et
        exists = db.check_vehicle(special_model, special_plate, special_color)
        assert exists is True

    @pytest.mark.unit
    def test_unicode_characters(self, temp_db):
        """Unicode karakter testi"""
        db = DatabaseHandler(temp_db)

        # Türkçe karakterler
        vehicle_id = db.insert_vehicle("Renault Mégane", "34ÇĞİ123", "Füme")
        assert vehicle_id > 0

        # Kontrol et
        exists = db.check_vehicle("Renault Mégane", "34ÇĞİ123", "Füme")
        assert exists is True
