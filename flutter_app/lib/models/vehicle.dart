class Vehicle {
  final String markaModel;
  final String plaka;
  final String renk;
  final String imagePath;
  final DateTime tarih;

  Vehicle({
    required this.markaModel,
    required this.plaka,
    required this.renk,
    required this.imagePath,
    required this.tarih,
  });

  Map<String, dynamic> toMap() {
    return {
      'marka_model': markaModel,
      'plaka': plaka,
      'renk': renk,
      'image_path': imagePath,
      'tarih': tarih.toIso8601String(),
    };
  }

  factory Vehicle.fromMap(Map<String, dynamic> map) {
    return Vehicle(
      markaModel: map['marka_model'],
      plaka: map['plaka'],
      renk: map['renk'],
      imagePath: map['image_path'] ?? '',
      tarih: DateTime.parse(map['tarih']),
    );
  }
}

class RecognitionResult {
  final String markaModel;
  final String renk;
  final String? plaka;
  final bool isMatch;
  final String message;

  RecognitionResult({
    required this.markaModel,
    required this.renk,
    this.plaka,
    required this.isMatch,
    required this.message,
  });
}
