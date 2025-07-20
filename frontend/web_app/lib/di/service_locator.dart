// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:get_it/get_it.dart';

import '../services/auth_service.dart';
import '../services/token_service.dart';

final GetIt locator = GetIt.instance;
final String url = String.fromEnvironment('API_URL');

void setupLocator() {
  locator.registerLazySingleton<Dio>(() {
    final dio = Dio(BaseOptions(baseUrl: url));
// api_URL can be your servers URL e.g: 'http://localhost:7087/api/'
    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        // Add JWT token to request headers
        final token = await locator<TokenService>().getToken();
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));
    return dio;
  });



  locator.registerLazySingleton<AuthService>(() => AuthService(locator<Dio>()));
  locator.registerLazySingleton<TokenService>(() => TokenService());
  locator.registerLazySingleton<FlutterSecureStorage>(() => FlutterSecureStorage());

}