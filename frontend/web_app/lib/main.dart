import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:web_app/provider/auth_provider.dart';
import 'package:web_app/services/auth_service.dart';
import 'package:web_app/viewmodels/login_viewmodel.dart';
import 'app/home_app.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

// Start app
void main() async {
   runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(AuthService(Dio()))),
        ChangeNotifierProvider(create: (_) => LoginViewModel()),
        // other providers...
      ],
      child: const MainApp(),
    ),
  );
}