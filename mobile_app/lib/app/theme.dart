import 'package:flutter/material.dart';

ThemeData buildPyxisTheme() {
  const seedColor = Color(0xFF174A5B);
  return ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: seedColor),
    useMaterial3: true,
  );
}
