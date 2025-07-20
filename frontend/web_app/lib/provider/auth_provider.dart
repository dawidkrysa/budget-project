// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'package:flutter/cupertino.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService;
  bool _isAuthenticated = false;


  AuthProvider(this._authService);

  bool get isAuthenticated => _isAuthenticated;

  Future<bool> login(String login, String password) async {
    var success = await _authService.login(login, password);
    print(success);
    if (success) {
      _isAuthenticated = true;
      // await _updateUser();
      notifyListeners();
    }
    return success;
  }

  Future<bool> signup(String name, String email, String login, String password) async {
    bool success = await _authService.signup(name, email, login, password);
    print(success);
    if (success) {
      _isAuthenticated = true;
      // await _updateUser();
      notifyListeners();
    }
    return success;
  }

  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    // _user = null;
    notifyListeners();
  }


}