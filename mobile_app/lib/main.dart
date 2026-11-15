import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'theme/miku_theme.dart';
import 'screens/scanner_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  runApp(const AkariRetailApp());
}

class AkariRetailApp extends StatelessWidget {
  const AkariRetailApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Akari Retail - Hatsune Miku Edition',
      debugShowCheckedModeBanner: false,
      theme: MikuTheme.themeData,
      home: const ScannerScreen(),
    );
  }
}
