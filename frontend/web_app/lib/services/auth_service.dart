// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'dart:convert'; // for jsonEncode, json.decode, utf8
import 'package:dio/dio.dart'; // for Dio HTTP client
import 'package:jwt_decoder/jwt_decoder.dart';
import 'package:universal_html/html.dart' as html;
import 'token_service.dart';

const String url = String.fromEnvironment('API_URL');

class AuthService {
  Dio _dio = Dio();
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
        final cookies = html.document.cookie?.split('; ') ?? [];
        print(html.document.cookie);
        for (var cookie in cookies) {
          if (cookie.startsWith('access_token=')) {
            final token = cookie.substring('access_token='.length);
            print('Token from cookie: $token');
            return true;
          }
        }
        return false;
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
            'login': login,
            'password': password,
          },
          options: Options(
              contentType: Headers.formUrlEncodedContentType
          )
      );

      if (response.statusCode == 200) {
        final cookies = html.document.cookie?.split('; ') ?? [];
        for (var cookie in cookies) {
          if (cookie.startsWith('access_token=')) {
            final token = cookie.substring('access_token='.length);
            print('Token from cookie: $token');
            return true;
          }
        }
        return false;
    }
    } catch (e) {
      print('Signup error: $e');
    }
    return false;
  }

    Future<void> logout() async {
      print('Logged out and token deleted');
    }

  Future<bool> hasValidToken() async {
    final cookies = html.document.cookie?.split('; ') ?? [];
        for (var cookie in cookies) {
          if (cookie.startsWith('access_token=')) {
            final token = cookie.substring('access_token='.length);
            final isExpired = JwtDecoder.isExpired(token);
            return !isExpired;
            print('Token from cookie: $token');
          }
        }
    return false;
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