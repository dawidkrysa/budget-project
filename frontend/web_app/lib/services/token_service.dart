// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

// Manages JWTs and related operations.
class TokenService {
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  Future<void> saveToken(String token) async {
    await _storage.write(key: 'jwt', value: token);
  }

  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt');
  }

  Future<void> deleteToken() async {
    await _storage.delete(key: 'jwt');
  }
}