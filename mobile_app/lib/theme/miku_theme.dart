import 'package:flutter/material.dart';

class MikuTheme {
  // Official Hatsune Miku Palette
  static const Color teal = Color(0xFF39C5BB);
  static const Color darkTeal = Color(0xFF229E95);
  static const Color lightTeal = Color(0xFFE8F8F7);
  static const Color softBg = Color(0xFFF0F9F8);
  static const Color cardBg = Color(0xFFFFFFFF);
  static const Color pink = Color(0xFFFF66A1);
  static const Color darkSlate = Color(0xFF2B333E);
  static const Color borderTeal = Color(0xFFC8EBE7);

  static ThemeData get themeData {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: teal,
        primary: teal,
        secondary: pink,
        background: softBg,
        surface: cardBg,
      ),
      scaffoldBackgroundColor: softBg,
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: darkSlate),
        titleTextStyle: TextStyle(
          color: darkSlate,
          fontSize: 16,
          fontWeight: FontWeight.w800,
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: teal,
          foregroundColor: Colors.white,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFFF7FCFB),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: borderTeal),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: borderTeal),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: const BorderSide(color: teal, width: 2),
        ),
      ),
    );
  }
}
