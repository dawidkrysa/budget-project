import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import '../app/router.dart';
import '../provider/auth_provider.dart';

class SignupViewModel extends ChangeNotifier {
  final TextEditingController nameController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController loginController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  bool _isLoading = false;

  bool get isLoading => _isLoading;

  void setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  Future<void> signup(BuildContext context) async {
    final authProvider = Provider.of<AuthProvider>(context, listen: false);

    final login = loginController.text.trim();
    final name = nameController.text.trim();
    final email = emailController.text.trim();
    final password = passwordController.text.trim();

    if (login.isEmpty || password.isEmpty || name.isEmpty || email.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please fill all fields')),
      );
      return;
    }

    final bool emailValid =
    RegExp(r"^[a-zA-Z0-9.a-zA-Z0-9.!#$%&'*+-/=?^_`{|}~]+@[a-zA-Z0-9]+\.[a-zA-Z]+")
      .hasMatch(email);

    if (!emailValid) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Invalid email address')),
      );
      return;
    }

    setLoading(true);

    final success = await authProvider.signup(name, email, login, password);
    setLoading(false);

    if (!context.mounted) return;

    if (success) {
      context.go(AppRoutes.budget);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Sign up failed! Please try again.')),
      );
    }
  }

  // Called when object is removed from the tree
  @override
  void dispose() {
    loginController.dispose();
    passwordController.dispose();
    nameController.dispose();
    emailController.dispose();
    super.dispose();
  }
}