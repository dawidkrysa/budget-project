// Source: https://medium.com/@areesh-ali/building-a-secure-flutter-app-with-jwt-and-apis-e22ade2b2d5f
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../app/router.dart';
import '../provider/auth_provider.dart';

class LogoutViewModel extends ChangeNotifier {

  Future<void> logout(BuildContext context) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);
    authProvider.logout();
  }

}