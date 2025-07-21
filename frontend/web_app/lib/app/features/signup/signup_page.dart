import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../utils/screen_utils.dart';
import '../../../viewmodels/signup_viewmodel.dart';

class SignupPage extends StatefulWidget {
  const SignupPage({super.key});

  @override
  SignupPageState createState() => SignupPageState();
}

class SignupPageState extends State<SignupPage> {
  @override
  Widget build(BuildContext context) {
    final signupViewModel = Provider.of<SignupViewModel>(context);
    final inputWidth = LayoutUtils.getResponsiveInputWidth(context);


    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              SizedBox(height: 52),
              Text(
                'Nice to meet you!',
                style: TextStyle(
                  fontFamily: 'Poppins',
                  fontWeight: FontWeight.bold,
                  fontSize: 26,
                  color: Color(0xFF1C1C1C),
                ),
              ),
              SizedBox(height: 6),
              Text(
                'Sign Up to continue',
                style: TextStyle(
                  fontFamily: 'Poppins',
                  fontWeight: FontWeight.normal,
                  fontSize: 18,
                  color: Color(0xFF1C1C1C),
                ),
              ),
              SizedBox(height: 26),
              SizedBox(
              width: inputWidth,
              child: TextField(
                controller: signupViewModel.nameController,
                decoration: InputDecoration(
                  labelText: 'Name',
                  border: OutlineInputBorder(),
                ),
                ),
              ),
              SizedBox(height: 16),
              SizedBox(
              width: inputWidth,
              child: TextField(
                controller: signupViewModel.emailController,
                decoration: InputDecoration(
                  labelText: 'Email',
                  border: OutlineInputBorder(),
                ),
                ),
              ),
              SizedBox(height: 16),
              SizedBox(
              width: inputWidth,
              child: TextField(
                controller: signupViewModel.loginController,
                decoration: InputDecoration(
                  labelText: 'Username',
                  border: OutlineInputBorder(),
                ),
                ),
              ),
              SizedBox(height: 16),
              SizedBox(
              width: inputWidth,
              child: TextField(
                controller: signupViewModel.passwordController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Password',
                  border: OutlineInputBorder(),
                ),
                ),
              ),
              const SizedBox(height: 26),
              SizedBox(
                width: inputWidth,
                height: 49,
                child: signupViewModel.isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : ElevatedButton(
                        onPressed: () {
                          signupViewModel.signup(context);
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue.shade900,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(10),
                          ),
                        ),
                        child: Text(
                          'Sign Up',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
