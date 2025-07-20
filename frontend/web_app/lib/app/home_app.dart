import 'package:flutter/material.dart';
import 'router.dart';

class MainApp extends StatelessWidget {
  const MainApp({super.key});

  @override
  Widget build(BuildContext context) {
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