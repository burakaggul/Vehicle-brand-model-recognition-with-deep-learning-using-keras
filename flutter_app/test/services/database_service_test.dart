import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import '../../lib/services/database_service.dart';

void main() {
  late DatabaseService service;

  setUpAll(() {
    // FFI database factory'yi başlat (test için)
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  setUp(() async {
    // Her test için yeni database instance
    service = DatabaseService();
    await service.database; // Database'i başlat
    await service.clearDatabase(); // Temiz başla
  });

  tearDown(() async {
    await service.close();
  });

  group('DatabaseService Basic Operations', () {
    test('should initialize database', () async {
      final db = await service.database;

      expect(db, isNotNull);
      expect(db.isOpen, isTrue);
    });

    test('should insert vehicle', () async {
      final id = await service.insertVehicle(
        '2012_2014_Ford Focus Ön',
        '34ABC123',
        'Beyaz',
      );

      expect(id, greaterThan(0));
    });

    test('should check existing vehicle', () async {
      // Araç ekle
      await service.insertVehicle(
        '2012_2014_Ford Focus Ön',
        '34ABC123',
        'Beyaz',
      );

      // Kontrol et
      final exists = await service.checkVehicle(
        '2012_2014_Ford Focus Ön',
        '34ABC123',
        'Beyaz',
      );

      expect(exists, isTrue);
    });

    test('should return false for non-existing vehicle', () async {
      final exists = await service.checkVehicle(
        'NonExistent Model',
        '00XXX000',
        'Mavi',
      );

      expect(exists, isFalse);
    });

    test('should get all vehicles', () async {
      // Birkaç araç ekle
      await service.insertVehicle('Ford Focus Ön', '34ABC123', 'Beyaz');
      await service.insertVehicle('Honda Civic Ön', '06XYZ456', 'Siyah');

      final vehicles = await service.getAllVehicles();

      expect(vehicles.length, greaterThanOrEqualTo(2));
    });

    test('should search by plate', () async {
      await service.insertVehicle('Ford Focus', '34ABC123', 'Beyaz');
      await service.insertVehicle('Honda Civic', '34ABC456', 'Siyah');
      await service.insertVehicle('Toyota Corolla', '06XYZ789', 'Kırmızı');

      final results = await service.searchByPlate('34ABC');

      expect(results.length, equals(2));
      expect(results.every((v) => v['plaka'].contains('34ABC')), isTrue);
    });

    test('should delete vehicle', () async {
      final id = await service.insertVehicle('Test Model', '34TEST99', 'Yeşil');

      final deleted = await service.deleteVehicle(id);

      expect(deleted, greaterThan(0));

      // Kontrol et - silinmiş olmalı
      final exists = await service.checkVehicle('Test Model', '34TEST99', 'Yeşil');
      expect(exists, isFalse);
    });

    test('should return 0 when deleting non-existent vehicle', () async {
      final deleted = await service.deleteVehicle(99999);

      expect(deleted, equals(0));
    });

    test('should clear database', () async {
      // Veri ekle
      await service.insertVehicle('Test', '34ABC123', 'Beyaz');

      // Temizle
      await service.resetDatabase();

      // Sadece sample data olmalı
      final vehicles = await service.getAllVehicles();
      expect(vehicles, isNotEmpty); // Sample data ekleniyor
    });
  });

  group('DatabaseService SQL Injection Prevention', () {
    test('should prevent SQL injection with single quote', () async {
      // Örnek veri ekle
      await service.insertVehicle('Test Model', '34ABC123', 'Beyaz');

      // SQL injection denemesi
      final maliciousInput = "' OR '1'='1";

      final result = await service.checkVehicle(
        maliciousInput,
        '34ABC123',
        'Beyaz',
      );

      // False dönmeli çünkü malicious input gerçek bir model değil
      expect(result, isFalse);
    });

    test('should prevent SQL injection with DROP TABLE', () async {
      await service.insertVehicle('Test Model', '34ABC123', 'Beyaz');

      // DROP TABLE denemesi
      final maliciousInput = "'; DROP TABLE kayitli_araclar; --";

      final result = await service.checkVehicle(
        maliciousInput,
        '34ABC123',
        'Beyaz',
      );

      expect(result, isFalse);

      // Tablo hala var olmalı
      final vehicles = await service.getAllVehicles();
      expect(vehicles, isNotNull);
    });

    test('should prevent SQL injection with UNION', () async {
      final maliciousInput = "' UNION SELECT * FROM kayitli_araclar --";

      final result = await service.checkVehicle(
        maliciousInput,
        'test',
        'test',
      );

      expect(result, isFalse);
    });

    test('should handle special characters safely', () async {
      // Özel karakterler içeren veri
      final specialModel = "Ford's \"Special\" Model";
      final specialPlate = "34-ABC-123";
      final specialColor = "Beyaz&Gri";

      final id = await service.insertVehicle(
        specialModel,
        specialPlate,
        specialColor,
      );

      expect(id, greaterThan(0));

      // Kontrol et
      final exists = await service.checkVehicle(
        specialModel,
        specialPlate,
        specialColor,
      );

      expect(exists, isTrue);
    });

    test('should handle Unicode characters', () async {
      final id = await service.insertVehicle(
        'Renault Mégane',
        '34ÇĞİ123',
        'Füme',
      );

      expect(id, greaterThan(0));

      final exists = await service.checkVehicle(
        'Renault Mégane',
        '34ÇĞİ123',
        'Füme',
      );

      expect(exists, isTrue);
    });

    test('should prevent SQL injection in searchByPlate', () async {
      await service.insertVehicle('Test', '34ABC123', 'Beyaz');

      // SQL injection denemesi
      final maliciousInput = "34ABC%'; DROP TABLE kayitli_araclar; --";

      final results = await service.searchByPlate(maliciousInput);

      // Hata vermemeli, güvenli şekilde işlemeli
      expect(results, isNotNull);
    });
  });

  group('DatabaseService Sample Data', () {
    test('should add sample data', () async {
      await service.clearDatabase();

      // Sample data zaten ekleniyor clearDatabase'de
      final vehicles = await service.getAllVehicles();

      expect(vehicles.length, greaterThanOrEqualTo(5));
    });

    test('sample data should have correct structure', () async {
      final vehicles = await service.getAllVehicles();

      expect(vehicles.isNotEmpty, isTrue);

      final vehicle = vehicles.first;
      expect(vehicle.containsKey('id'), isTrue);
      expect(vehicle.containsKey('marka_model'), isTrue);
      expect(vehicle.containsKey('plaka'), isTrue);
      expect(vehicle.containsKey('renk'), isTrue);
    });
  });

  group('DatabaseService Edge Cases', () {
    test('should handle empty strings', () async {
      final id = await service.insertVehicle('', '', '');

      expect(id, greaterThan(0));
    });

    test('should handle very long strings', () async {
      final longString = 'A' * 1000;

      final id = await service.insertVehicle(
        longString,
        longString,
        longString,
      );

      expect(id, greaterThan(0));
    });

    test('should handle concurrent operations', () async {
      // Eşzamanlı insert işlemleri
      final futures = List.generate(
        10,
        (i) => service.insertVehicle(
          'Model $i',
          '34ABC${i.toString().padLeft(3, '0')}',
          'Beyaz',
        ),
      );

      final results = await Future.wait(futures);

      expect(results.every((id) => id > 0), isTrue);
      expect(results.toSet().length, equals(10)); // Hepsi farklı ID olmalı
    });

    test('should handle database close and reopen', () async {
      await service.insertVehicle('Test', '34ABC123', 'Beyaz');

      await service.close();

      // Yeni service instance
      service = DatabaseService();

      final exists = await service.checkVehicle('Test', '34ABC123', 'Beyaz');
      expect(exists, isTrue);
    });
  });

  group('DatabaseService Performance', () {
    test('should handle large number of records', () async {
      // 100 kayıt ekle
      for (int i = 0; i < 100; i++) {
        await service.insertVehicle(
          'Model $i',
          '34${i.toString().padLeft(5, '0')}',
          'Beyaz',
        );
      }

      final vehicles = await service.getAllVehicles();

      expect(vehicles.length, greaterThanOrEqualTo(100));
    }, timeout: Timeout(Duration(seconds: 30)));

    test('search should be fast with many records', () async {
      // Birçok kayıt ekle
      for (int i = 0; i < 50; i++) {
        await service.insertVehicle(
          'Model $i',
          '34ABC${i.toString().padLeft(3, '0')}',
          'Beyaz',
        );
      }

      final stopwatch = Stopwatch()..start();
      final results = await service.searchByPlate('34ABC');
      stopwatch.stop();

      expect(results.length, greaterThan(0));
      expect(stopwatch.elapsedMilliseconds, lessThan(1000)); // 1 saniyeden az
    });
  });
}
