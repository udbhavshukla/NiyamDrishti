import 'package:flutter/material.dart';
import 'scan_screen.dart';

// This screen has no changing data, so it's a StatelessWidget - the
// simplest kind of screen in Flutter.
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('NiyamDrishti AI - Inspector')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.fact_check, size: 80, color: Colors.indigo),
            const SizedBox(height: 16),
            const Text(
              'Legal Metrology Compliance Scanner',
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 32),
            ElevatedButton.icon(
              icon: const Icon(Icons.qr_code_scanner),
              label: const Text('Start New Scan'),
              onPressed: () {
                // Navigator.push takes us to a NEW screen and puts it
                // on top of this one (so the back button works automatically).
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const ScanScreen()),
                );
              },
            ),
          ],
        ),
      ),
    );
  }
}
