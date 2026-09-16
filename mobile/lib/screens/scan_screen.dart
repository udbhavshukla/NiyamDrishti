import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../api_service.dart';
import 'result_screen.dart';

// This screen has data that CHANGES (which images the inspector picked),
// so it must be a StatefulWidget.
class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});

  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  // One nullable File per required image. "null" means "not picked yet".
  File? frontLabelImage;
  File? mrpImage;
  File? manufacturerImage;

  bool isSubmitting = false; // controls the loading UI

  final ImagePicker picker = ImagePicker();

  // Shows a small dialog asking Camera or Gallery, then picks from
  // whichever the inspector chose, and saves the picked file into the
  // right slot using the "onPicked" callback so we can reuse this one
  // function for all three image types.
  Future<void> pickImage(Function(File) onPicked) async {
    final ImageSource? source = await showDialog<ImageSource>(
      context: context,
      builder: (context) => SimpleDialog(
        title: const Text('Choose Image Source'),
        children: [
          SimpleDialogOption(
            onPressed: () => Navigator.pop(context, ImageSource.camera),
            child: const Row(children: [Icon(Icons.camera_alt), SizedBox(width: 12), Text('Camera')]),
          ),
          SimpleDialogOption(
            onPressed: () => Navigator.pop(context, ImageSource.gallery),
            child: const Row(children: [Icon(Icons.photo_library), SizedBox(width: 12), Text('Gallery')]),
          ),
        ],
      ),
    );

    if (source == null) return; // inspector dismissed the dialog without choosing

    final XFile? picked = await picker.pickImage(source: source);
    if (picked != null) {
      setState(() {
        onPicked(File(picked.path));
      });
    }
  }

  // --- Basic image quality feedback ---
  // NOTE: This is a simple placeholder check (file size only).
  // Real blur/glare/quality detection belongs to Member 1 (AI/OCR team).
  // This just gives the inspector an early, obvious warning before upload.
  String? checkImageQuality(File image) {
    final sizeInKb = image.lengthSync() / 1024;
    if (sizeInKb < 20) {
      return 'Image looks very small - please retake for a clearer scan.';
    }
    return null; // null means "looks fine"
  }

  // All three images must be picked before we allow submitting.
  bool get allImagesReady =>
      frontLabelImage != null && mrpImage != null && manufacturerImage != null;

  Future<void> submitForCompliance() async {
    setState(() => isSubmitting = true);

    // This calls our FAKE backend for now. See mock_api.dart -
    // this is the exact line Member 3's real API call will replace.
    final result = await submitImagesForCompliance(
      frontLabelImage: frontLabelImage!,
      mrpImage: mrpImage!,
      manufacturerImage: manufacturerImage!,
    );

    setState(() => isSubmitting = false);

    if (!mounted) return; // safety check - screen might have closed while waiting
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => ResultScreen(result: result)),
    );
  }

  @override
  Widget build(BuildContext context) {
    // While waiting for the (mock) backend, show a full-screen loading state
    // instead of the normal scan form.
    if (isSubmitting) {
      return Scaffold(
        appBar: AppBar(title: const Text('Processing...')),
        body: const Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(),
              SizedBox(height: 16),
              Text('Checking compliance, please wait...'),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Scan Package')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          imageSlot('1. Front Label', frontLabelImage, (file) => frontLabelImage = file),
          const SizedBox(height: 16),
          imageSlot('2. MRP Panel', mrpImage, (file) => mrpImage = file),
          const SizedBox(height: 16),
          imageSlot('3. Manufacturer Details', manufacturerImage, (file) => manufacturerImage = file),
          const SizedBox(height: 24),
          ElevatedButton(
            // Button is disabled (null) until all 3 images exist.
            onPressed: allImagesReady ? submitForCompliance : null,
            child: const Text('Submit for Compliance Check'),
          ),
        ],
      ),
    );
  }

  // One reusable "card" for each of the 3 required images:
  // shows a placeholder or preview, a quality warning, and a pick/retake button.
  Widget imageSlot(String title, File? image, Function(File) onPicked) {
    final warning = image != null ? checkImageQuality(image) : null;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (image == null)
              const Icon(Icons.image_outlined, size: 60, color: Colors.grey)
            else
              Image.file(image, height: 120, fit: BoxFit.cover),
            if (warning != null)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(warning, style: const TextStyle(color: Colors.orange)),
              ),
            const SizedBox(height: 8),
            OutlinedButton.icon(
              icon: const Icon(Icons.camera_alt),
              label: Text(image == null ? 'Capture / Upload' : 'Retake'),
              onPressed: () => pickImage(onPicked),
            ),
          ],
        ),
      ),
    );
  }
}
