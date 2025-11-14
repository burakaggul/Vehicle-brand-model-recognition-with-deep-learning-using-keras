import 'dart:io';
import 'package:google_ml_kit/google_ml_kit.dart';

class PlateRecognitionService {
  final _textRecognizer = TextRecognizer();

  /// Görüntüden plaka metnini oku
  Future<String?> recognizePlate(String imagePath) async {
    try {
      print('Plaka okunuyor...');

      // Görüntüyü yükle
      final inputImage = InputImage.fromFilePath(imagePath);

      // Metni tanı
      final RecognizedText recognizedText = await _textRecognizer.processImage(inputImage);

      // Tüm metni birleştir
      String fullText = recognizedText.text;
      print('Okunan ham metin: $fullText');

      // Plaka formatını temizle
      String? plate = _cleanPlateText(fullText);

      if (plate != null && plate.isNotEmpty) {
        print('✓ Plaka tespit edildi: $plate');
        return plate;
      } else {
        print('⚠ Plaka tespit edilemedi');
        return null;
      }
    } catch (e) {
      print('❌ Plaka okuma hatası: $e');
      return null;
    }
  }

  /// Plaka metnini temizle ve formatla
  String? _cleanPlateText(String text) {
    // Boşlukları, noktalama işaretlerini vb. kaldır (Python kodundaki regex'in aynısı)
    // re.sub('\ |\?|\.|\!|\/|\\|\;|\:|\'|\(|\)|\-|\{|\}|\]|\[|\&|\,|\'|\||\»|\¢|\*|\§|\°|','',t_plaka)
    String cleaned = text.replaceAll(RegExp(r'[ \?\.\!\/\\\;\:\'\(\)\-\{\}\]\[\&\,\|\»\¢\*\§\°]'), '');

    // Sadece harf ve rakamları al
    cleaned = cleaned.replaceAll(RegExp(r'[^A-Z0-9]'), '');

    // Türk plaka formatını kontrol et (örn: 34ABC1234)
    if (_isValidTurkishPlate(cleaned)) {
      return cleaned;
    }

    // Alternatif: En uzun alfanumerik diziyi bul
    final matches = RegExp(r'[A-Z0-9]{5,}').allMatches(cleaned);
    if (matches.isNotEmpty) {
      return matches.first.group(0);
    }

    return cleaned.isNotEmpty ? cleaned : null;
  }

  /// Türk plaka formatını kontrol et
  bool _isValidTurkishPlate(String plate) {
    // Basit format kontrolü: 2 rakam + 1-3 harf + 1-4 rakam
    // Örnek: 34ABC123, 06XYZ9999
    final plateRegex = RegExp(r'^[0-9]{2}[A-Z]{1,3}[0-9]{1,4}$');
    return plateRegex.hasMatch(plate);
  }

  /// Gelişmiş plaka tespiti (görüntü işleme ile)
  Future<String?> recognizePlateAdvanced(String imagePath) async {
    try {
      // Görüntüyü yükle
      final inputImage = InputImage.fromFilePath(imagePath);

      // Metni tanı
      final RecognizedText recognizedText = await _textRecognizer.processImage(inputImage);

      // Tüm text block'ları kontrol et
      String? bestPlate;
      double bestConfidence = 0.0;

      for (TextBlock block in recognizedText.blocks) {
        for (TextLine line in block.lines) {
          String lineText = line.text.toUpperCase();
          String cleaned = _cleanPlateText(lineText);

          if (cleaned != null && cleaned.length >= 6) {
            // Plaka benzeri metni değerlendir
            double confidence = _evaluatePlateConfidence(cleaned);

            if (confidence > bestConfidence) {
              bestConfidence = confidence;
              bestPlate = cleaned;
            }
          }
        }
      }

      if (bestPlate != null && bestConfidence > 0.5) {
        print('✓ En iyi plaka adayı: $bestPlate (Güven: ${(bestConfidence * 100).toStringAsFixed(1)}%)');
        return bestPlate;
      }

      return null;
    } catch (e) {
      print('❌ Gelişmiş plaka okuma hatası: $e');
      return null;
    }
  }

  /// Plaka güven skorunu hesapla
  double _evaluatePlateConfidence(String text) {
    double score = 0.0;

    // Uzunluk kontrolü (7-10 karakter ideal)
    if (text.length >= 7 && text.length <= 10) {
      score += 0.3;
    }

    // Türk plaka formatı kontrolü
    if (_isValidTurkishPlate(text)) {
      score += 0.5;
    }

    // Rakam ve harf dengesi
    int letterCount = text.replaceAll(RegExp(r'[^A-Z]'), '').length;
    int digitCount = text.replaceAll(RegExp(r'[^0-9]'), '').length;

    if (letterCount >= 1 && letterCount <= 3 && digitCount >= 3 && digitCount <= 6) {
      score += 0.2;
    }

    return score > 1.0 ? 1.0 : score;
  }

  /// Kaynakları temizle
  void dispose() {
    _textRecognizer.close();
  }
}
