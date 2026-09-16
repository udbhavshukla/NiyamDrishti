import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

// Every Flutter app starts by running a widget - here, our whole App.
void main() {
  runApp(const NiyamDrishtiApp());
}

class NiyamDrishtiApp extends StatelessWidget {
  const NiyamDrishtiApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'NiyamDrishti AI - Inspector',
      theme: ThemeData(primarySwatch: Colors.indigo, useMaterial3: true),
      debugShowCheckedModeBanner: false,
      home: const HomeScreen(), // first screen shown
    );
  }
}
