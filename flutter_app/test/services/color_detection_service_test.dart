import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'dart:io';
import 'package:path/path.dart' as path;
import '../../lib/services/color_detection_service.dart';

void main() {
  late ColorDetectionService service;
  late Directory tempDir;

  setUp(() {
    service = ColorDetectionService();
    tempDir = Directory.systemTemp.createTempSync('color_test_');
  });

  tearDown(() {
    // Cleanup
    if (tempDir.existsSync()) {
      tempDir.deleteSync(recursive: true);
    }
  });

  group('ColorDetectionService Tests', () {
    test('should detect white color', () async {
      // Beyaz araç görüntüsü oluştur
      final image = img.Image(600, 450);
      img.fill(image, img.getColor(240, 240, 235));

      final imagePath = path.join(tempDir.path, 'white_car.jpg');
      File(imagePath).writeAsBytesSync(img.encodeJpg(image));

      final color = await service.detectVehicleColor(imagePath);

      expect(color, equals('Beyaz'));
    });

    test('should detect black color', () async {
      // Siyah araç görüntüsü oluştur
      final image = img.Image(600, 450);
      img.fill(image, img.getColor(50, 50, 50));

      final imagePath = path.join(tempDir.path, 'black_car.jpg');
      File(imagePath).writeAsBytesSync(img.encodeJpg(image));

      final color = await service.detectVehicleColor(imagePath);

      expect(color, equals('Siyah'));
    });

    test('should detect red color', () async {
      // Kırmızı araç görüntüsü oluştur (BGR formatında)
      final image = img.Image(600, 450);

      // Kırmızı bölgeler oluştur
      for (int y = 100; y < 250; y++) {
        for (int x = 100; x < 600; x++) {
          image.setPixelRgba(x, y, 180, 50, 50, 255);
        }
      }

      final imagePath = path.join(tempDir.path, 'red_car.jpg');
      File(imagePath).writeAsBytesSync(img.encodeJpg(image));

      final color = await service.detectVehicleColor(imagePath);

      expect(color, equals('Kırmızı'));
    });

    test('should return Bilinmiyor for invalid image', () async {
      final color = await service.detectVehicleColor('nonexistent.jpg');

      expect(color, equals('Bilinmiyor'));
    });

    test('should classify white color correctly', () {
      final color = service._classifyColor(200, 200, 200);

      expect(color, equals('Beyaz'));
    });

    test('should classify black color correctly', () {
      final color = service._classifyColor(50, 50, 50);

      expect(color, equals('Siyah'));
    });

    test('should classify füme color correctly', () {
      final color = service._classifyColor(130, 130, 130);

      expect(color, equals('Füme'));
    });

    test('should classify gri color correctly', () {
      final color = service._classifyColor(160, 165, 165);

      expect(color, equals('Gri'));
    });

    test('should classify lacivert color correctly', () {
      final color = service._classifyColor(50, 80, 180);

      expect(color, equals('Lacivert'));
    });

    test('should classify red color correctly', () {
      final color = service._classifyColor(180, 50, 50);

      expect(color, equals('Kırmızı'));
    });

    test('should return Diğer for unclassified color', () {
      final color = service._classifyColor(75, 200, 100);

      expect(color, equals('Diğer'));
    });

    test('should handle boundary values for white', () {
      // Alt sınır
      expect(service._classifyColor(170, 180, 180), equals('Beyaz'));

      // Üst sınır
      expect(service._classifyColor(254, 254, 254), equals('Beyaz'));
    });

    test('should handle boundary values for black', () {
      // Sınır değeri
      expect(service._classifyColor(110, 109, 110), equals('Siyah'));

      // Minimum
      expect(service._classifyColor(0, 0, 0), equals('Siyah'));
    });

    test('should handle pure colors', () {
      // Saf beyaz
      expect(service._classifyColor(255, 255, 255), equals('Beyaz'));

      // Saf siyah
      expect(service._classifyColor(0, 0, 0), equals('Siyah'));
    });

    test('getPixelRGB should return correct RGB values', () {
      final image = img.Image(100, 100);

      // Kırmızı piksel ayarla
      image.setPixelRgba(50, 50, 255, 0, 0, 255);

      final rgb = service.getPixelRGB(image, 50, 50);

      expect(rgb['r'], equals(255));
      expect(rgb['g'], equals(0));
      expect(rgb['b'], equals(0));
    });
  });

  group('Color Detection Edge Cases', () {
    test('should handle very small images', () async {
      final image = img.Image(10, 10);
      img.fill(image, img.getColor(200, 200, 200));

      final imagePath = path.join(tempDir.path, 'small.jpg');
      File(imagePath).writeAsBytesSync(img.encodeJpg(image));

      final color = await service.detectVehicleColor(imagePath);

      expect(color, isNotNull);
    });

    test('should handle very large images', () async {
      final image = img.Image(2000, 1500);
      img.fill(image, img.getColor(50, 50, 50));

      final imagePath = path.join(tempDir.path, 'large.jpg');
      File(imagePath).writeAsBytesSync(img.encodeJpg(image));

      final color = await service.detectVehicleColor(imagePath);

      expect(color, equals('Siyah'));
    });
  });
}
