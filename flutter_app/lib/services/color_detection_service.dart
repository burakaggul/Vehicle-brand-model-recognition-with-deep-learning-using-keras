import 'dart:io';
import 'package:image/image.dart' as img;

class ColorDetectionService {
  /// Görüntüden araç rengini tespit et
  Future<String> detectVehicleColor(String imagePath) async {
    try {
      // Görüntüyü oku
      final imageBytes = await File(imagePath).readAsBytes();
      img.Image? image = img.decodeImage(imageBytes);

      if (image == null) {
        throw Exception('Görüntü okunamadı');
      }

      // Resize (600x450) - orijinal Python kodundaki gibi
      img.Image resizedImage = img.copyResize(
        image,
        width: 600,
        height: 450,
      );

      // İki bölgeden renk örneği al (orijinal koddaki gibi)
      // cropped_1 = image_color[100:250, 100:350]
      // cropped_2 = image_color[100:250, 350:600]

      // Bölge 1: (y: 100-250, x: 100-350)
      final rgb1 = _getAverageRGB(resizedImage, 100, 350, 100, 250);

      // Bölge 2: (y: 100-250, x: 350-600)
      final rgb2 = _getAverageRGB(resizedImage, 350, 600, 100, 250);

      // Ortalamaları hesapla
      final avgR = ((rgb1['r']! + rgb2['r']!) / 2).round();
      final avgG = ((rgb1['g']! + rgb2['g']!) / 2).round();
      final avgB = ((rgb1['b']! + rgb2['b']!) / 2).round();

      print('Renk RGB değerleri: R=$avgR, G=$avgG, B=$avgB');

      // Rengi belirle (orijinal Python kodundaki mantık)
      final color = _classifyColor(avgR, avgG, avgB);

      return color;
    } catch (e) {
      print('❌ Renk tespiti hatası: $e');
      return 'Bilinmiyor';
    }
  }

  /// Belirli bir bölgedeki ortalama RGB değerlerini hesapla
  Map<String, int> _getAverageRGB(
    img.Image image,
    int startX,
    int endX,
    int startY,
    int endY,
  ) {
    int totalR = 0, totalG = 0, totalB = 0;
    int pixelCount = 0;

    for (int y = startY; y < endY && y < image.height; y++) {
      for (int x = startX; x < endX && x < image.width; x++) {
        final pixel = image.getPixel(x, y);
        totalR += pixel.r.toInt();
        totalG += pixel.g.toInt();
        totalB += pixel.b.toInt();
        pixelCount++;
      }
    }

    return {
      'r': pixelCount > 0 ? (totalR / pixelCount).round() : 0,
      'g': pixelCount > 0 ? (totalG / pixelCount).round() : 0,
      'b': pixelCount > 0 ? (totalB / pixelCount).round() : 0,
    };
  }

  /// RGB değerlerine göre renk sınıflandır (Python kodunun aynısı)
  String _classifyColor(int r, int g, int b) {
    // Beyaz
    if (b >= 180 && b < 255 && g >= 180 && g < 255 && r >= 170 && r < 255) {
      return "Beyaz";
    }
    // Füme
    else if (b > 110 && b < 150 && g > 110 && g < 150 && r > 110 && r < 150) {
      return "Füme";
    }
    // Gri
    else if (b > 150 && b < 180 && g > 150 && g < 180 && r > 150 && r < 170) {
      return "Gri";
    }
    // Lacivert
    else if (b > 130 && b < 255 && g > 25 && g < 150 && r > 0 && r < 150) {
      return "Lacivert";
    }
    // Kırmızı
    else if (b > 0 && b < 150 && g > 0 && g < 150 && r > 100 && r < 255) {
      return "Kırmızı";
    }
    // Siyah
    else if (b <= 110 && g < 110 && r < 110) {
      return "Siyah";
    }
    // Varsayılan
    else {
      return "Diğer";
    }
  }

  /// Debug için: görüntünün belirli bir pikselinin RGB değerini al
  Map<String, int> getPixelRGB(img.Image image, int x, int y) {
    final pixel = image.getPixel(x, y);
    return {
      'r': pixel.r.toInt(),
      'g': pixel.g.toInt(),
      'b': pixel.b.toInt(),
    };
  }
}
