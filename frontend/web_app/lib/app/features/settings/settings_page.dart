import 'package:flutter/material.dart';
import '../../../utils/screen_utils.dart';

class SettingsPage extends StatelessWidget {
  const SettingsPage({super.key});

  @override
  Widget build(BuildContext context) {
    final inputWidth = LayoutUtils.getResponsiveInputWidth(context);

    return Center(child: Text('Nice to meet you!'));
  }
}
