import 'package:flutter/cupertino.dart';

class LayoutUtils {
  /// Returns the input field width based on screen size.
  ///
  /// - On wide screens (>600), it uses 20% of screen width.
  /// - On small screens (≤600), it uses full width minus horizontal padding.
  static double getResponsiveInputWidth(BuildContext context, {double padding = 30}) {
    final screenWidth = MediaQuery.of(context).size.width;

    if (screenWidth > 600) {
      return screenWidth * 0.2;
    } else {
      return screenWidth - (padding * 2);
    }
  }
}