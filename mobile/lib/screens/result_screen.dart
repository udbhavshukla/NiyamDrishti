import 'package:flutter/material.dart';
import '../models.dart';

// This screen just DISPLAYS data it was given - it never changes its own
// data - so it can be a simple StatelessWidget.
class ResultScreen extends StatelessWidget {
  final ComplianceResult result;

  // "required this.result" means whoever creates this screen MUST pass
  // in a ComplianceResult - this is how data moves from ScanScreen to here.
  const ResultScreen({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Compliance Result')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            color: Colors.indigo.shade50,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text('Overall Status', style: TextStyle(fontSize: 14, color: Colors.grey)),
                  Text(
                    result.overallStatus,
                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          const Text('Declarations Checked', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 8),
          // A "for" loop inside a list of widgets - Dart lets us build this
          // list by looping over result.declarations, one row per item.
          for (final declaration in result.declarations) declarationRow(declaration),
        ],
      ),
    );
  }

  Widget declarationRow(Declaration declaration) {
    return Card(
      child: ListTile(
        title: Text(declaration.name),
        subtitle: declaration.value != null ? Text('Detected: ${declaration.value}') : null,
        trailing: statusBadge(declaration.status),
      ),
    );
  }

  // Turns a DeclarationStatus into a small colored label - this is
  // the visual language requirement #11 asked for.
  Widget statusBadge(DeclarationStatus status) {
    late String label;
    late Color color;

    // "switch" picks one branch based on the enum value - reads like
    // a decision table, which matches how the rule engine team thinks too.
    switch (status) {
      case DeclarationStatus.found:
        label = 'FOUND';
        color = Colors.green;
        break;
      case DeclarationStatus.missing:
        label = 'MISSING';
        color = Colors.red;
        break;
      case DeclarationStatus.unclear:
        label = 'UNCLEAR';
        color = Colors.orange;
        break;
      case DeclarationStatus.needsReview:
        label = 'NEEDS REVIEW';
        color = Colors.blueGrey;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(12)),
      child: Text(label, style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}
