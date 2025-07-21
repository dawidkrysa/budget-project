import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../provider/auth_provider.dart';
import 'router.dart';

class MainApp extends StatelessWidget {
  const MainApp({super.key});


  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context, listen: true);
    final router = createRouter(authProvider);

    return MaterialApp.router(
      title: 'Home budget',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: Colors.blue.shade900,
          brightness: Brightness.light,
        ),
      ),
      routerConfig: router,
    );
  }
}