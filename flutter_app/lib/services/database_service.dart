import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/vehicle.dart';

class DatabaseService {
  static Database? _database;
  static const String _databaseName = 'vehicle_recognition.db';
  static const String _tableName = 'kayitli_araclar';

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await initDatabase();
    return _database!;
  }

  /// Veritabanını başlat
  Future<Database> initDatabase() async {
    try {
      final dbPath = await getDatabasesPath();
      final path = join(dbPath, _databaseName);

      print('Veritabanı oluşturuluyor: $path');

      final database = await openDatabase(
        path,
        version: 1,
        onCreate: _createDatabase,
      );

      print('✓ Veritabanı başlatıldı');
      return database;
    } catch (e) {
      print('❌ Veritabanı başlatma hatası: $e');
      rethrow;
    }
  }

  /// Veritabanı tablolarını oluştur
  Future<void> _createDatabase(Database db, int version) async {
    // Kayıtlı araçlar tablosu (Python kodundaki test.db ile aynı)
    await db.execute('''
      CREATE TABLE $_tableName (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        marka_model TEXT NOT NULL,
        plaka TEXT NOT NULL,
        renk TEXT NOT NULL,
        kayit_tarihi TEXT DEFAULT CURRENT_TIMESTAMP
      )
    ''');

    // Örnek veri ekle
    await _insertSampleData(db);

    print('✓ Veritabanı tabloları oluşturuldu');
  }

  /// Örnek veri ekle (test için)
  Future<void> _insertSampleData(Database db) async {
    final sampleVehicles = [
      {
        'marka_model': '2012_2014_Ford Focus Ön',
        'plaka': '34ABC123',
        'renk': 'Beyaz',
      },
      {
        'marka_model': '2012_2014_Ford Focus Arka',
        'plaka': '34ABC123',
        'renk': 'Beyaz',
      },
      {
        'marka_model': '2016_2019_Honda Civic Ön',
        'plaka': '06XYZ456',
        'renk': 'Siyah',
      },
      {
        'marka_model': '2016_2019_Honda Civic Arka',
        'plaka': '06XYZ456',
        'renk': 'Siyah',
      },
      {
        'marka_model': '2012_2014_Ford Focus Ön',
        'plaka': '35TEST99',
        'renk': 'Kırmızı',
      },
    ];

    for (var vehicle in sampleVehicles) {
      await db.insert(_tableName, vehicle);
    }

    print('✓ ${sampleVehicles.length} örnek kayıt eklendi');
  }

  /// Araç bilgilerini sorgula (Python kodundaki SQL sorgusu)
  Future<bool> checkVehicle(String markaModel, String plaka, String renk) async {
    try {
      final db = await database;

      // Python kodundaki sorgu:
      // SELECT * FROM kayitli_araclar where marka_model='...' and plaka='...' and renk='...'
      final List<Map<String, dynamic>> results = await db.query(
        _tableName,
        where: 'marka_model = ? AND plaka = ? AND renk = ?',
        whereArgs: [markaModel, plaka, renk],
      );

      if (results.isNotEmpty) {
        print('✓ Araç veritabanında bulundu: ${results.first}');
        return true;
      } else {
        print('⚠ Araç veritabanında bulunamadı');
        return false;
      }
    } catch (e) {
      print('❌ Veritabanı sorgulama hatası: $e');
      return false;
    }
  }

  /// Yeni araç ekle
  Future<int> insertVehicle(String markaModel, String plaka, String renk) async {
    try {
      final db = await database;

      final id = await db.insert(_tableName, {
        'marka_model': markaModel,
        'plaka': plaka,
        'renk': renk,
      });

      print('✓ Yeni araç eklendi (ID: $id)');
      return id;
    } catch (e) {
      print('❌ Araç ekleme hatası: $e');
      return -1;
    }
  }

  /// Tüm kayıtlı araçları getir
  Future<List<Map<String, dynamic>>> getAllVehicles() async {
    try {
      final db = await database;
      final results = await db.query(_tableName, orderBy: 'kayit_tarihi DESC');
      return results;
    } catch (e) {
      print('❌ Araç listesi getirme hatası: $e');
      return [];
    }
  }

  /// Plakaya göre araç ara
  Future<List<Map<String, dynamic>>> searchByPlate(String plaka) async {
    try {
      final db = await database;
      final results = await db.query(
        _tableName,
        where: 'plaka LIKE ?',
        whereArgs: ['%$plaka%'],
      );
      return results;
    } catch (e) {
      print('❌ Plaka arama hatası: $e');
      return [];
    }
  }

  /// Araç sil
  Future<int> deleteVehicle(int id) async {
    try {
      final db = await database;
      final count = await db.delete(
        _tableName,
        where: 'id = ?',
        whereArgs: [id],
      );
      print('✓ Araç silindi (ID: $id)');
      return count;
    } catch (e) {
      print('❌ Araç silme hatası: $e');
      return 0;
    }
  }

  /// Veritabanını sıfırla (tüm kayıtları sil)
  Future<void> resetDatabase() async {
    try {
      final db = await database;
      await db.delete(_tableName);
      await _insertSampleData(db);
      print('✓ Veritabanı sıfırlandı');
    } catch (e) {
      print('❌ Veritabanı sıfırlama hatası: $e');
    }
  }

  /// Veritabanını kapat
  Future<void> close() async {
    if (_database != null) {
      await _database!.close();
      _database = null;
      print('✓ Veritabanı kapatıldı');
    }
  }
}
