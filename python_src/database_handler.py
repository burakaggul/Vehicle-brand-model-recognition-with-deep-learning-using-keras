#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Veritabanı İşlemleri Modülü
Database Handler Module - SQL Injection Korumalı
"""

import sqlite3
from typing import Optional, List, Dict, Tuple
from contextlib import contextmanager
import os


class DatabaseHandler:
    """
    Güvenli veritabanı işlemleri için sınıf
    SQL Injection koruması ile parametrize sorgular kullanır
    """

    def __init__(self, db_path: str = 'vehicle_recognition.db'):
        """
        DatabaseHandler sınıfını başlatır

        Args:
            db_path: Veritabanı dosya yolu
        """
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        """
        Veritabanı bağlantısı için context manager

        Yields:
            sqlite3.Connection: Veritabanı bağlantısı
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Dict-like access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _init_database(self):
        """Veritabanını ve tabloları oluşturur"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Kayıtlı araçlar tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS kayitli_araclar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    marka_model TEXT NOT NULL,
                    plaka TEXT NOT NULL,
                    renk TEXT NOT NULL,
                    kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(marka_model, plaka, renk)
                )
            ''')

            # İndeks oluştur (performans için)
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_plaka
                ON kayitli_araclar(plaka)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_marka_model
                ON kayitli_araclar(marka_model)
            ''')

            conn.commit()

    def check_vehicle(self, marka_model: str, plaka: str, renk: str) -> bool:
        """
        Araç bilgilerini veritabanında kontrol eder (SQL Injection Korumalı)

        Args:
            marka_model: Araç marka ve model bilgisi
            plaka: Araç plakası
            renk: Araç rengi

        Returns:
            True: Araç bulundu
            False: Araç bulunamadı
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # GÜVENLI: Parametrize sorgu kullanıyoruz (SQL Injection korumalı)
            query = '''
                SELECT * FROM kayitli_araclar
                WHERE marka_model = ? AND plaka = ? AND renk = ?
            '''

            cursor.execute(query, (marka_model, plaka, renk))
            result = cursor.fetchone()

            return result is not None

    def get_vehicle(self, marka_model: str, plaka: str, renk: str) -> Optional[Dict]:
        """
        Araç bilgilerini getirir

        Args:
            marka_model: Araç marka ve model bilgisi
            plaka: Araç plakası
            renk: Araç rengi

        Returns:
            Araç bilgileri dict veya None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT * FROM kayitli_araclar
                WHERE marka_model = ? AND plaka = ? AND renk = ?
            '''

            cursor.execute(query, (marka_model, plaka, renk))
            result = cursor.fetchone()

            if result:
                return dict(result)
            return None

    def insert_vehicle(self, marka_model: str, plaka: str, renk: str) -> int:
        """
        Yeni araç kaydı ekler

        Args:
            marka_model: Araç marka ve model bilgisi
            plaka: Araç plakası
            renk: Araç rengi

        Returns:
            Eklenen kaydın ID'si

        Raises:
            sqlite3.IntegrityError: Kayıt zaten varsa
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                INSERT INTO kayitli_araclar (marka_model, plaka, renk)
                VALUES (?, ?, ?)
            '''

            cursor.execute(query, (marka_model, plaka, renk))
            return cursor.lastrowid

    def search_by_plate(self, plaka: str) -> List[Dict]:
        """
        Plakaya göre araç arar

        Args:
            plaka: Araç plakası (kısmi arama destekler)

        Returns:
            Bulunan araçların listesi
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = '''
                SELECT * FROM kayitli_araclar
                WHERE plaka LIKE ?
                ORDER BY kayit_tarihi DESC
            '''

            cursor.execute(query, (f'%{plaka}%',))
            results = cursor.fetchall()

            return [dict(row) for row in results]

    def get_all_vehicles(self) -> List[Dict]:
        """
        Tüm kayıtlı araçları getirir

        Returns:
            Araç listesi
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = 'SELECT * FROM kayitli_araclar ORDER BY kayit_tarihi DESC'
            cursor.execute(query)
            results = cursor.fetchall()

            return [dict(row) for row in results]

    def delete_vehicle(self, vehicle_id: int) -> bool:
        """
        Araç kaydını siler

        Args:
            vehicle_id: Silinecek aracın ID'si

        Returns:
            True: Silme başarılı
            False: Kayıt bulunamadı
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            query = 'DELETE FROM kayitli_araclar WHERE id = ?'
            cursor.execute(query, (vehicle_id,))

            return cursor.rowcount > 0

    def add_sample_data(self):
        """Test için örnek veri ekler"""
        sample_vehicles = [
            ("2012_2014_Ford Focus Ön", "34ABC123", "Beyaz"),
            ("2012_2014_Ford Focus Arka", "34ABC123", "Beyaz"),
            ("2016_2019_Honda Civic Ön", "06XYZ456", "Siyah"),
            ("2016_2019_Honda Civic Arka", "06XYZ456", "Siyah"),
            ("2012_2014_Ford Focus Ön", "35TEST99", "Kırmızı"),
        ]

        for marka_model, plaka, renk in sample_vehicles:
            try:
                self.insert_vehicle(marka_model, plaka, renk)
            except sqlite3.IntegrityError:
                # Kayıt zaten var, atla
                pass

    def clear_database(self):
        """Tüm kayıtları siler (TEST AMAÇLI)"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM kayitli_araclar')
            conn.commit()

    def get_statistics(self) -> Dict:
        """
        Veritabanı istatistiklerini döndürür

        Returns:
            İstatistik bilgileri
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Toplam araç sayısı
            cursor.execute('SELECT COUNT(*) FROM kayitli_araclar')
            total_count = cursor.fetchone()[0]

            # Renk dağılımı
            cursor.execute('''
                SELECT renk, COUNT(*) as count
                FROM kayitli_araclar
                GROUP BY renk
                ORDER BY count DESC
            ''')
            color_distribution = [dict(row) for row in cursor.fetchall()]

            # Marka dağılımı
            cursor.execute('''
                SELECT marka_model, COUNT(*) as count
                FROM kayitli_araclar
                GROUP BY marka_model
                ORDER BY count DESC
            ''')
            brand_distribution = [dict(row) for row in cursor.fetchall()]

            return {
                'total_vehicles': total_count,
                'color_distribution': color_distribution,
                'brand_distribution': brand_distribution
            }
