// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'package:flutter/foundation.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService;
  bool _isAuthenticated = false;
  bool _isLoading = true;

  AuthProvider(this._authService){
    _initializeAuth();
  }

  bool get isAuthenticated => _isAuthenticated;
  bool get isLoading => _isLoading;

  Future<void> _initializeAuth() async {
    _isAuthenticated = await _authService.hasValidToken();
    _isLoading = false;
    notifyListeners();
  }

  Future<bool> login(String login, String password) async {
    var success = await _authService.login(login, password);
    if (success) {
      _isAuthenticated = true;
      notifyListeners();
    }
    return success;
  }

  Future<bool> signup(String name, String email, String login, String password) async {
    bool success = await _authService.signup(name, email, login, password);
    if (success) {
      _isAuthenticated = true;
      notifyListeners();
    }
    return success;
  }

  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    notifyListeners();
  }


}