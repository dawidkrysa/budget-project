import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:web_app/provider/auth_provider.dart';
import 'package:web_app/provider/budget_provider.dart';
import 'package:web_app/provider/transaction_provider.dart';
import 'package:web_app/services/auth_service.dart';
import 'package:web_app/services/budget_service.dart';
import 'package:web_app/services/transaction_service.dart';
import 'package:web_app/viewmodels/login_viewmodel.dart';
import 'package:web_app/viewmodels/logout_viewmodel.dart';
import 'package:web_app/viewmodels/signup_viewmodel.dart';
import 'app/home_app.dart';

// Start app
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

   runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider(AuthService(Dio()))),
        ChangeNotifierProvider(create: (_) => LoginViewModel()),
        ChangeNotifierProvider(create: (_) => SignupViewModel()),
        ChangeNotifierProvider(create: (_) => LogoutViewModel()),
        ChangeNotifierProvider(create: (_) => BudgetProvider(BudgetService())),
        ChangeNotifierProvider(create: (_) => TransactionProvider(TransactionService())),
        // other providers...
      ],
      child: const MainApp(),
    ),
  );
}