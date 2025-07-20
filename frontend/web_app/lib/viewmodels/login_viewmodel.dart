// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../provider/auth_provider.dart';

class LoginViewModel extends ChangeNotifier {
  final TextEditingController loginController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  bool _isLoading = false;

  bool get isLoading => _isLoading;

  void setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  Future<void> login(BuildContext context) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    final login = loginController.text.trim();
    final password = passwordController.text.trim();

    if (login.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please fill all fields')),
      );
      return;
    }

    setLoading(true);

    final success = await authProvider.login(login, password);
    setLoading(false);

    if (success) {
      context.go('/budget');
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Login failed! Please try again.')),
      );
    }
  }

  @override
  void dispose() {
    loginController.dispose();
    passwordController.dispose();
    super.dispose();
  }
}