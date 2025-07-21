import 'package:flutter/foundation.dart';

class DebugUtils {
  static void log(String message) {
    if (kDebugMode) {
      print(message);
    }
  }
}