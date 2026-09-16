// This file just defines the SHAPE of the data we expect from the backend.
// Member 3 (Backend) will eventually send real JSON matching this shape.
// For now, mock_api.dart fills it with fake data.

// An "enum" is a fixed list of allowed values - safer than using plain strings,
// because Dart won't let you accidentally type "FOND" instead of "FOUND".
enum DeclarationStatus { found, missing, unclear, needsReview }

// One line item in the compliance report, e.g. "MRP -> FOUND -> ₹199"
class Declaration {
  final String name; // e.g. "Maximum Retail Price"
  final DeclarationStatus status;
  final String? value; // the detected text, if any (nullable - may not exist)

  Declaration({required this.name, required this.status, this.value});
}

// The full result for one scanned package.
class ComplianceResult {
  final String overallStatus; // e.g. "NEEDS REVIEW"
  final List<Declaration> declarations;

  ComplianceResult({required this.overallStatus, required this.declarations});
}
