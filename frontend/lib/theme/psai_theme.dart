import 'package:flutter/material.dart';

/// Visual identity for P.S.AI — warm parchment tones over dark backgrounds,
/// evoking a scholar's study illuminated by lamplight.
class PSAITheme {
  PSAITheme._();

  // ── Palette ────────────────────────────────────────────────────
  static const Color _midnight = Color(0xFF0D1117);
  static const Color _obsidian = Color(0xFF161B22);
  static const Color _slate = Color(0xFF21262D);
  static const Color _ash = Color(0xFF30363D);
  static const Color _fog = Color(0xFF8B949E);
  static const Color _parchment = Color(0xFFF0E6D3);
  static const Color _gold = Color(0xFFD4A843);
  static const Color _copper = Color(0xFFC97B4B);
  static const Color _sage = Color(0xFF7EAA7E);
  static const Color _error = Color(0xFFCF6679);

  // ── Theme ──────────────────────────────────────────────────────
  static ThemeData get dark => ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: _midnight,
        colorScheme: const ColorScheme.dark(
          primary: _gold,
          secondary: _copper,
          tertiary: _sage,
          surface: _obsidian,
          error: _error,
          onPrimary: _midnight,
          onSecondary: _midnight,
          onSurface: _parchment,
          onError: _midnight,
        ),
        cardTheme: CardTheme(
          color: _obsidian,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: _ash, width: 0.5),
          ),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: _obsidian,
          foregroundColor: _parchment,
          elevation: 0,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: _slate,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: _ash),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: _ash),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: const BorderSide(color: _gold, width: 1.5),
          ),
          hintStyle: const TextStyle(color: _fog),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: _gold,
            foregroundColor: _midnight,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          ),
        ),
        chipTheme: ChipThemeData(
          backgroundColor: _slate,
          selectedColor: _gold.withValues(alpha: 0.25),
          labelStyle: const TextStyle(color: _parchment, fontSize: 13),
          side: const BorderSide(color: _ash),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
        dividerTheme: const DividerThemeData(color: _ash, thickness: 0.5),
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            color: _parchment,
            fontSize: 28,
            fontWeight: FontWeight.w300,
            letterSpacing: 1.2,
          ),
          headlineMedium: TextStyle(
            color: _parchment,
            fontSize: 22,
            fontWeight: FontWeight.w400,
          ),
          titleMedium: TextStyle(
            color: _gold,
            fontSize: 16,
            fontWeight: FontWeight.w500,
          ),
          bodyLarge: TextStyle(color: _parchment, fontSize: 15, height: 1.6),
          bodyMedium: TextStyle(color: _fog, fontSize: 14, height: 1.5),
          labelSmall: TextStyle(
            color: _fog,
            fontSize: 11,
            letterSpacing: 1.0,
          ),
        ),
      );
}
