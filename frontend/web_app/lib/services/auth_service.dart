// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'dart:convert'; // for jsonEncode, json.decode, utf8
import 'package:dio/dio.dart'; // for Dio HTTP client
import 'package:jwt_decoder/jwt_decoder.dart';
import 'package:web_app/services/token_service.dart';
import 'package:web_app/utils/debug_utils.dart';

const String url = String.fromEnvironment('API_URL');

class AuthService {
  final Dio _dio;
  final TokenService _tokenService = TokenService();

  AuthService(this._dio);

  Future<bool> login(String login, String password) async {
    try {
      final response = await _dio.post(
        '$url/auth/login',
        data: {'login': login, 'password': password},
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      if (response.statusCode == 200) {
        final token = response.data['token']; // Expect token from API
        if (token != null) {
          await _tokenService.saveToken(token);
          DebugUtils.log('Token saved: $token');
          return true;
        }
      }
    } catch (e) {
      DebugUtils.log('Login error: $e');
    }
    return false;
  }

  Future<bool> signup(
    String name,
    String email,
    String login,
    String password,
  ) async {
    try {
      final response = await _dio.post(
        '$url/auth/signup',
        data: {
          'name': name,
          'email': email,
          'login': login,
          'password': password,
        },
        options: Options(contentType: Headers.formUrlEncodedContentType),
      );

      if (response.statusCode == 200) {
        final token = response.data['token']; // Expect token from API
        if (token != null) {
          await _tokenService.saveToken(token);
          DebugUtils.log('Token saved: $token');
          return true;
        }
      }
    } catch (e) {
      DebugUtils.log('Signup error: $e');
    }
    return false;
  }

  Future<void> logout() async {
    await _tokenService.deleteToken();
    DebugUtils.log('Logged out and token deleted');
  }

  Future<bool> hasValidToken() async {
    final token = await _tokenService.getToken();
    if (token != null && !JwtDecoder.isExpired(token)) {
      return true;
    }
    return false;
  }

  Map<String, dynamic> parseJwt(String token) {
    final parts = token.split('.');
    if (parts.length != 3) {
      throw Exception('Invalid token');
    }
    final payload = utf8.decode(
      base64Url.decode(base64Url.normalize(parts[1])),
    );
    return json.decode(payload);
  }
}
