import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/model_service.dart';
import '../services/color_detection_service.dart';
import '../services/plate_recognition_service.dart';
import '../services/database_service.dart';

class RecognitionScreen extends StatefulWidget {
  final String imagePath;

  const RecognitionScreen({super.key, required this.imagePath});

  @override
  State<RecognitionScreen> createState() => _RecognitionScreenState();
}

class _RecognitionScreenState extends State<RecognitionScreen> {
  bool _isProcessing = false;
  String? _markaModel;
  String? _renk;
  String? _plaka;
  bool? _isMatch;
  String? _message;
  double? _confidence;

  final ModelService _modelService = ModelService();
  final ColorDetectionService _colorService = ColorDetectionService();
  final PlateRecognitionService _plateService = PlateRecognitionService();

  @override
  void initState() {
    super.initState();
    _initializeAndProcess();
  }

  Future<void> _initializeAndProcess() async {
    setState(() => _isProcessing = true);

    try {
      // Modeli yükle
      await _modelService.loadModel();

      // Analiz yap
      await _processImage();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Hata: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isProcessing = false);
      }
    }
  }

  Future<void> _processImage() async {
    try {
      // 1. Marka/Model Tahmini
      final prediction = await _modelService.predictVehicle(widget.imagePath);
      _markaModel = prediction['label'];
      _confidence = prediction['confidence'];

      // 2. Renk Tespiti
      _renk = await _colorService.detectVehicleColor(widget.imagePath);

      // 3. Plaka Okuma
      _plaka = await _plateService.recognizePlateAdvanced(widget.imagePath);

      // 4. Veritabanında Kontrol
      if (_markaModel != null && _renk != null && _plaka != null) {
        final dbService = Provider.of<DatabaseService>(context, listen: false);
        _isMatch = await dbService.checkVehicle(_markaModel!, _plaka!, _renk!);

        if (_isMatch == true) {
          _message = 'Araç Marka Model, Plaka ve Renk Bilgisi Eşleşti!';
        } else {
          _message = 'Eşleşme Başarısız. Araç veritabanında bulunamadı.';
        }
      } else {
        _message = 'Bazı bilgiler tespit edilemedi.';
        _isMatch = false;
      }

      setState(() {});
    } catch (e) {
      print('❌ İşleme hatası: $e');
      setState(() {
        _message = 'İşleme sırasında hata oluştu: $e';
        _isMatch = false;
      });
    }
  }

  @override
  void dispose() {
    _modelService.dispose();
    _plateService.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Analiz Sonucu'),
        backgroundColor: Colors.blue.shade700,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Görüntü
            Container(
              width: double.infinity,
              height: 300,
              color: Colors.grey.shade200,
              child: Image.file(
                File(widget.imagePath),
                fit: BoxFit.contain,
              ),
            ),

            // Yükleniyor göstergesi
            if (_isProcessing)
              Padding(
                padding: const EdgeInsets.all(32.0),
                child: Column(
                  children: [
                    CircularProgressIndicator(
                      valueColor: AlwaysStoppedAnimation<Color>(Colors.blue.shade700),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Analiz ediliyor...',
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                  ],
                ),
              ),

            // Sonuçlar
            if (!_isProcessing) ...[
              // Eşleşme durumu
              if (_message != null)
                Container(
                  margin: const EdgeInsets.all(16),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: _isMatch == true ? Colors.green.shade50 : Colors.red.shade50,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: _isMatch == true ? Colors.green : Colors.red,
                      width: 2,
                    ),
                  ),
                  child: Row(
                    children: [
                      Icon(
                        _isMatch == true ? Icons.check_circle : Icons.cancel,
                        color: _isMatch == true ? Colors.green : Colors.red,
                        size: 32,
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _message!,
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: _isMatch == true ? Colors.green.shade900 : Colors.red.shade900,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

              // Detay bilgileri
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Column(
                  children: [
                    _buildResultCard(
                      icon: Icons.directions_car,
                      title: 'Marka/Model',
                      value: _markaModel ?? 'Tespit edilemedi',
                      subtitle: _confidence != null
                          ? 'Güven: ${(_confidence! * 100).toStringAsFixed(1)}%'
                          : null,
                    ),
                    const SizedBox(height: 12),
                    _buildResultCard(
                      icon: Icons.palette,
                      title: 'Renk',
                      value: _renk ?? 'Tespit edilemedi',
                    ),
                    const SizedBox(height: 12),
                    _buildResultCard(
                      icon: Icons.credit_card,
                      title: 'Plaka',
                      value: _plaka ?? 'Tespit edilemedi',
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Tekrar dene butonu
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.refresh),
                    label: const Text('Yeni Analiz'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue.shade700,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard({
    required IconData icon,
    required String title,
    required String value,
    String? subtitle,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.shade50,
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: Colors.blue.shade700, size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey.shade500,
                    ),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
