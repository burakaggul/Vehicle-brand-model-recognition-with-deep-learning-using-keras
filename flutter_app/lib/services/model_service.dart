import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/services.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart';

class ModelService {
  Interpreter? _interpreter;
  List<String> _labels = [];
  bool _isModelLoaded = false;

  // Model input shape
  static const int inputHeight = 600;
  static const int inputWidth = 450;
  static const int channels = 3;

  bool get isModelLoaded => _isModelLoaded;

  /// Modeli yükle
  Future<void> loadModel() async {
    try {
      print('Model yükleniyor...');

      // TFLite modelini yükle
      _interpreter = await Interpreter.fromAsset('assets/models/model.tflite');

      // Etiketleri yükle
      await _loadLabels();

      _isModelLoaded = true;
      print('✓ Model başarıyla yüklendi');
      print('  Input shape: ${_interpreter?.getInputTensors().first.shape}');
      print('  Output shape: ${_interpreter?.getOutputTensors().first.shape}');
    } catch (e) {
      print('❌ Model yükleme hatası: $e');
      _isModelLoaded = false;
      rethrow;
    }
  }

  /// Etiketleri yükle
  Future<void> _loadLabels() async {
    try {
      final labelsData = await rootBundle.loadString('assets/models/labels.txt');
      _labels = labelsData.split('\n').where((label) => label.isNotEmpty).toList();
      print('✓ ${_labels.length} etiket yüklendi');
    } catch (e) {
      print('⚠ Etiket dosyası yüklenemedi: $e');
      // Varsayılan etiketler
      _labels = [
        "2012_2014_Ford Focus Ön",
        "2012_2014_Ford Focus Arka",
        "2016_2019_Honda Civic Ön",
        "2016_2019_Honda Civic Arka",
      ];
    }
  }

  /// Görüntüden araç marka/model tahmini yap
  Future<Map<String, dynamic>> predictVehicle(String imagePath) async {
    if (!_isModelLoaded || _interpreter == null) {
      throw Exception('Model yüklenmedi!');
    }

    try {
      // Görüntüyü yükle ve ön işle
      final inputImage = await _preprocessImage(imagePath);

      // Output buffer oluştur
      var outputBuffer = List.filled(1 * _labels.length, 0.0).reshape([1, _labels.length]);

      // Tahmin yap
      _interpreter!.run(inputImage, outputBuffer);

      // Sonuçları işle
      final predictions = outputBuffer[0] as List<double>;
      final maxIndex = predictions.indexOf(predictions.reduce((a, b) => a > b ? a : b));
      final confidence = predictions[maxIndex];

      print('Tahmin: ${_labels[maxIndex]} (Güven: ${(confidence * 100).toStringAsFixed(2)}%)');

      return {
        'label': _labels[maxIndex],
        'confidence': confidence,
        'classIndex': maxIndex,
        'allPredictions': predictions,
      };
    } catch (e) {
      print('❌ Tahmin hatası: $e');
      rethrow;
    }
  }

  /// Görüntüyü model için ön işle
  Future<List<List<List<List<double>>>>> _preprocessImage(String imagePath) async {
    // Görüntüyü oku
    final imageBytes = await File(imagePath).readAsBytes();
    img.Image? image = img.decodeImage(imageBytes);

    if (image == null) {
      throw Exception('Görüntü okunamadı');
    }

    // Resize (600x450)
    img.Image resizedImage = img.copyResize(
      image,
      width: inputWidth,
      height: inputHeight,
    );

    // Normalize edilmiş pixel değerlerini oluştur (0-1 arası)
    var input = List.generate(
      1,
      (_) => List.generate(
        inputHeight,
        (y) => List.generate(
          inputWidth,
          (x) {
            final pixel = resizedImage.getPixel(x, y);
            return [
              pixel.r / 255.0, // Red
              pixel.g / 255.0, // Green
              pixel.b / 255.0, // Blue
            ];
          },
        ),
      ),
    );

    return input;
  }

  /// Kaynakları temizle
  void dispose() {
    _interpreter?.close();
    _isModelLoaded = false;
  }
}
