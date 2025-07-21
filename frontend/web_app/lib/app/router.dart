import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import '../provider/auth_provider.dart';
import './features/budget/budget_page.dart';
import './features/transactions/transactions_page.dart';
import './features/settings/settings_page.dart';
import './features/accounts/accounts_page.dart';
import './features/reports/reports_page.dart';
import './features/login/login_page.dart';
import 'navigation.dart';

final router = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    // Access AuthProvider without listening to changes
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    // Wait for auth state to load before redirecting
    if (authProvider.isLoading) return null;

    final loggedIn = authProvider.isAuthenticated;

    print('Zalogowany $loggedIn');
    print('Lokalizacja ${state.matchedLocation}');

    // If not logged in and trying to access anything other than login, redirect to login
    if (!loggedIn && state.matchedLocation != '/') return '/';

    // If logged in and trying to go to login page, redirect to first protected page
    if (loggedIn && state.matchedLocation == '/') return AppRoutes.routes[0];

    // Otherwise no redirect
    return null;
  },
  routes: [
    // LOGIN route (no navigation shell)
    GoRoute(
          path: '/',
          builder: (context, state) => const LoginPage(),
        ),
    ShellRoute(
      builder: (context, state, child) {
        return NavigationScaffold(child: child);
      },
      routes: [
        GoRoute(
          path: AppRoutes.routes[0],
          builder: (context, state) => const BudgetPage(),
        ),
        GoRoute(
          path: AppRoutes.routes[1],
          builder: (context, state) => const TransactionsPage(),
        ),
        GoRoute(
          path: AppRoutes.routes[2],
          builder: (context, state) => const AccountsPage(),
        ),
         GoRoute(
          path: AppRoutes.routes[3],
          builder: (context, state) => const ReportsPage(),
        ),
        GoRoute(
          path: AppRoutes.routes[4],
          builder: (context, state) => const SettingsPage(),
        ),
      ],
    ),
  ],
);

class AppRoutes {
  // Getting access without creating an instance, immutable
  static const List<String> routes = [
    '/budget',
    '/transactions',
    '/accounts',
    '/reports',
    '/settings'
  ];
}