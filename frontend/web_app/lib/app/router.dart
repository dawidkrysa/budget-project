import 'package:go_router/go_router.dart';
import 'package:web_app/utils/debug_utils.dart';
import '../provider/auth_provider.dart';
import './features/budget/budget_page.dart';
import './features/transactions/transactions_page.dart';
import './features/settings/settings_page.dart';
import './features/accounts/accounts_page.dart';
import './features/reports/reports_page.dart';
import './features/login/login_page.dart';
import './features/signup/signup_page.dart';
import 'navigation.dart';

GoRouter createRouter(AuthProvider authProvider) {
  return GoRouter(
    initialLocation: AppRoutes.login,
    refreshListenable: authProvider,
    redirect: (context, state) {
      DebugUtils.log(
        'Redirect: isLoading=${authProvider.isLoading}, isAuthenticated=${authProvider.isAuthenticated}, path=${state.uri.path}',
      );
      if (authProvider.isLoading) return null;

      final loggedIn = authProvider.isAuthenticated;
      final path = state.uri.path;

      const publicRoutes = {AppRoutes.login, AppRoutes.signup};
      const privateRoutes = {
        AppRoutes.budget,
        AppRoutes.transactions,
        AppRoutes.accounts,
        AppRoutes.reports,
        AppRoutes.settings,
      };

      // Redirect unauthenticated users to login if accessing protected routes
      if (!loggedIn && !publicRoutes.contains(path)) {
        return AppRoutes.login;
      }

      // If logged in and on a private route, stay (no redirect)
      if (loggedIn && privateRoutes.contains(path)) {
        return null;
      }

      // Redirect logged-in users from public routes to budget
      if (loggedIn && publicRoutes.contains(path)) {
        return AppRoutes.budget;
      }

      // Default: no redirect
      return null;
    },
    routes: [
      // LOGIN route (no navigation shell)
      GoRoute(
        path: AppRoutes.login,
        builder: (context, state) => const LoginPage(),
      ),
      GoRoute(
        path: AppRoutes.signup,
        builder: (context, state) => const SignupPage(),
      ),
      ShellRoute(
        builder: (context, state, child) {
          return NavigationScaffold(child: child);
        },
        routes: [
          GoRoute(
            path: AppRoutes.budget,
            builder: (context, state) => const BudgetPage(),
          ),
          GoRoute(
            path: AppRoutes.transactions,
            builder: (context, state) => const TransactionsPage(),
          ),
          GoRoute(
            path: AppRoutes.accounts,
            builder: (context, state) => const AccountsPage(),
          ),
          GoRoute(
            path: AppRoutes.reports,
            builder: (context, state) => const ReportsPage(),
          ),
          GoRoute(
            path: AppRoutes.settings,
            builder: (context, state) => const SettingsPage(),
          ),
        ],
      ),
    ],
  );
}

class AppRoutes {
  // Getting access without creating an instance, immutable
  static const String budget = '/budget';
  static const String transactions = '/transactions';
  static const String accounts = '/accounts';
  static const String reports = '/reports';
  static const String settings = '/settings';
  static const String signup = '/signup';
  static const String login = '/';

  static const List<String> shellRoutes = [
    budget,
    transactions,
    accounts,
    reports,
    settings,
  ];
}
