import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'package:web_app/app/router.dart';
import 'package:web_app/viewmodels/logout_viewmodel.dart';

// Widget can be built and might change during the lifetime
class NavigationScaffold extends StatelessWidget {
  final Widget child;
  const NavigationScaffold({required this.child, super.key});

  // Scaffold is base layout where all information are provided
  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).uri.toString();
    int selectedIndex = AppRoutes.shellRoutes.indexOf(location);

    final destinations = _buildDestinations();

    Widget navigationRail = NavigationRail(
      selectedIndex: selectedIndex,
      onDestinationSelected: (index) {
        Navigator.of(context).maybePop(); // Closes drawer if open
        // If logout (last destination), trigger logout
        if (index == AppRoutes.shellRoutes.length) {
          final logoutViewModel = Provider.of<LogoutViewModel>(
            context,
            listen: false,
          );
          logoutViewModel.logout(context);
          return;
        }
        context.go(AppRoutes.shellRoutes[index]);
      },
      labelType: NavigationRailLabelType.all,
      leading: const SizedBox(height: 16),
      destinations: destinations,
    );

    return LayoutBuilder(
      builder: (context, constraints) {
        final isPhone = constraints.maxWidth < 600;
        if (isPhone) {
          return Scaffold(
            appBar: AppBar(
              leading: Builder(
                builder: (context) => IconButton(
                  icon: const Icon(Icons.menu),
                  onPressed: () => Scaffold.of(context).openDrawer(),
                ),
              ),
            ),
            drawer: Drawer(
              width: MediaQuery.of(context).size.width * 0.4,
              child: SafeArea(child: navigationRail),
            ),
            body: child,
          );
        } else {
          return Scaffold(
            body: Row(
              children: [
                navigationRail,
                const VerticalDivider(thickness: 1, width: 1),
                Expanded(child: child),
              ],
            ),
          );
        }
      },
    );
  }
}

List<NavigationRailDestination> _buildDestinations() => const [
  NavigationRailDestination(
    padding: EdgeInsets.all(16.0),
    icon: Icon(Icons.home_outlined),
    selectedIcon: Icon(Icons.home),
    label: Text('Budget'),
  ),
  NavigationRailDestination(
    padding: EdgeInsets.all(16.0),
    icon: Icon(Icons.monetization_on_outlined),
    selectedIcon: Icon(Icons.monetization_on),
    label: Text('Transactions'),
  ),
  NavigationRailDestination(
    padding: EdgeInsets.all(16.0),
    icon: Icon(Icons.account_box_outlined),
    selectedIcon: Icon(Icons.account_box),
    label: Text('Accounts'),
  ),
  NavigationRailDestination(
    padding: EdgeInsets.all(16.0),
    icon: Icon(Icons.insert_chart_outlined_outlined),
    selectedIcon: Icon(Icons.insert_chart),
    label: Text('Reports'),
  ),
  NavigationRailDestination(
    padding: EdgeInsets.all(16.0),
    icon: Icon(Icons.settings_outlined),
    selectedIcon: Icon(Icons.settings),
    label: Text('Settings'),
  ),
  NavigationRailDestination(
    padding: EdgeInsets.all(16.0),
    icon: Icon(Icons.logout_outlined),
    selectedIcon: Icon(Icons.logout),
    label: Text('Logout'),
  ),
];
