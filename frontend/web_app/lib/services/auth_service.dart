// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'dart:convert'; // for jsonEncode, json.decode, utf8
import 'package:dio/dio.dart'; // for Dio HTTP client
import 'package:jwt_decoder/jwt_decoder.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart'; // for secure storage

const String url = String.fromEnvironment('API_URL');

class AuthService {
  Dio _dio = Dio();
  final FlutterSecureStorage _storage = FlutterSecureStorage();

  AuthService(this._dio);

  Future<bool> login(String login, String password) async {
    try {
      final response = await _dio.post(
          '$url/auth/login',
          data: {'login': login, 'password': password},
          options: Options(
              contentType: Headers.formUrlEncodedContentType
          )
      );

      if (response.statusCode == 200) {
        final token = response.data['token'];
        print(response.data);
        if (token != null) {
          await _storage.write(key: 'jwt', value: token);
          return true;
        }
      }
    } catch (e) {
      print('Login error: $e');
    }
    return false;
  }

  Future<bool> signup(String name, String email, String login,
      String password) async {
    try {
      final response = await _dio.post(
          '$url/auth/signup',
          data: {
            'name': name,
            'email': email,
            'confirmPassword': login,
            'password': password,
          },
          options: Options(
              contentType: Headers.formUrlEncodedContentType
          )
      );

      if (response.statusCode == 200) {
        final token = response.data; // Ensure this matches your API response
        if (token != null) {
          await _storage.write(key: 'jwt', value: token);
          return true;
        }
      }
    } catch (e) {
      print('Signup error: $e');
    }
    return false;
  }

  Future<String?> getToken() async {
    return await _storage.read(key: 'jwt');
  }

  Future<void> logout() async {
    await _storage.delete(key: 'jwt');
  }

  Future<bool> hasValidToken() async {
    final token = await getToken(); // SharedPreferences, etc.
    final isExpired = JwtDecoder.isExpired(token!);
    return !isExpired;
  }

  Map<String, dynamic> parseJwt(String token) {
    final parts = token.split('.');
    if (parts.length != 3) {
      throw Exception('Invalid token');
    }
    final payload =
    utf8.decode(base64Url.decode(base64Url.normalize(parts[1])));
    return json.decode(payload);
  }
}