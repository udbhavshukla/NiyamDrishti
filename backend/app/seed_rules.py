"""
Idempotent seed script for the 14 Legal Metrology rule records supplied by Member 2.

Run:
    python -m app.seed_rules

Safe to run multiple times — duplicate rule_id values are skipped.
"""

from __future__ import annotations

from datetime import datetime

from app.database import SessionLocal, create_tables
from app.models import Rule

RULES = [
    {
        "rule_id": "LM-PC-006-1A",
        "field_name": "MANUFACTURER_PACKER_IMPORTER_NAME_ADDRESS",
        "requirement_type": "mandatory_declaration",
        "requirement": "Every retail package must declare the name and complete address of the manufacturer; where the manufacturer is not the packer, the name and address of both manufacturer and packer; and for imported packages, the name and address of the importer.",
        "severity": "critical",
        "explanation": "Identifies the legally responsible party for the product; required for consumer redress and enforcement action.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(1)(a), read with Rule 10(1) and Explanations I & II to Rule 6(1)(a)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-1B",
        "field_name": "COMMODITY_COMMON_OR_GENERIC_NAME",
        "requirement_type": "mandatory_declaration",
        "requirement": "The common or generic name of the commodity contained in the package must be declared; if the package contains more than one product, the name and number/quantity of each must be stated.",
        "severity": "critical",
        "explanation": "Prevents mislabeling and helps consumers identify what they are buying.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(1)(b)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-1C",
        "field_name": "NET_QUANTITY",
        "requirement_type": "mandatory_declaration",
        "requirement": "The net quantity of the commodity in the package must be declared in terms of the standard unit of weight/measure, or, where sold by number, the number of items contained.",
        "severity": "critical",
        "explanation": "Core consumer-protection field; basis for price-per-unit comparison and for maximum-permissible-error checks under the First Schedule.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(1)(c), read with Rule 11, Rule 12 and the First Schedule",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-1D",
        "field_name": "MONTH_YEAR_OF_MANUFACTURE_PACKING_IMPORT",
        "requirement_type": "mandatory_declaration",
        "requirement": "The month and year in which the commodity was manufactured, pre-packed, or imported must be declared. Exemptions: bidis, incense sticks, and 14.2kg/5kg domestic LPG cylinders marketed by PSUs are exempt from this field entirely; spare parts/accessories used for warranty servicing (not sold to end customers) are exempt (w.e.f. 01-04-2024); for electronic products, spare parts and accessories, the date must be specified anywhere on the retail package, visibly and legibly (w.e.f. 01-04-2024). Food articles instead follow FSSAI labelling rules.",
        "severity": "high",
        "explanation": "Establishes shelf-life/freshness context and supports traceability during inspections.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(1)(d) and provisos thereto, as amended by the Legal Metrology (Packaged Commodities) Amendment Rules, 2023 (notified 06-10-2023, this clause effective 01-04-2024)",
        "effective_from": "2024-04-01",
        "effective_to": None,
        "version": "2",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-1E",
        "field_name": "MRP_RETAIL_SALE_PRICE",
        "requirement_type": "mandatory_declaration",
        "requirement": "The retail sale price (MRP), inclusive of all taxes, must be declared on the package in the form 'Maximum or Max. Retail Price Rs.___ inclusive of all taxes' (or 'MRP Rs.___ incl. of all taxes'), with paise rounding rules applied (below 50 paise rounded down, 50-95 paise rounded to 50 paise). Exceptions: bidis, and domestic LPG cylinders priced under the Administrative Price Mechanism, are exempt from this declaration.",
        "severity": "critical",
        "explanation": "Prevents overcharging and price ambiguity; the single most enforcement-sensitive field.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 2(m) (definition), Rule 6(1)(e), and Rule 6(1)(g) proviso (C)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-2",
        "field_name": "CONSUMER_CARE_DETAILS",
        "requirement_type": "mandatory_declaration",
        "requirement": "Every package must bear the name, address, telephone number, and e-mail address (if available) of the person/office that can be contacted for consumer complaints.",
        "severity": "high",
        "explanation": "Enables grievance redress; absence or unclear contact details is a common real-world violation.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(2)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-3",
        "field_name": "NO_STICKER_OVER_DECLARATION",
        "requirement_type": "prohibition",
        "requirement": "It is not permissible to affix individual stickers to alter or make a required declaration, EXCEPT a sticker reducing the MRP is allowed provided it does not cover the original manufacturer/packer MRP declaration.",
        "severity": "high",
        "explanation": "Detects a common tampering pattern -- stickers used to overwrite mandatory fields (MRP, mfg date, address).",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(3) and its proviso",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-007-FONT",
        "field_name": "FONT_READABILITY_MIN_HEIGHT",
        "requirement_type": "format_requirement",
        "requirement": "Minimum numeral height on the principal display panel scales with declared net quantity: up to 200g/ml -> 1mm (2mm if blown/molded/embossed); 200-500g/ml -> 2mm (4mm); above 500g/ml -> 4mm (6mm). Letter height in any declaration must not be less than 1mm (2mm if blown/molded/embossed), and letter/numeral width not less than one-third of its height (except '1', 'i', 'I', 'l').",
        "severity": "medium",
        "explanation": "Objective, measurable basis for flagging 'tiny/unreadable text' violations from OCR bounding-box dimensions.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 7(2), 7(3) and Tables I & II thereunder",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-009-LANG",
        "field_name": "DECLARATION_LANGUAGE",
        "requirement_type": "format_requirement",
        "requirement": "All mandatory declarations must be in Hindi (Devanagari script) or in English; other languages may be used in addition to, not instead of, Hindi/English.",
        "severity": "low",
        "explanation": "Used to flag packages whose mandatory fields appear only in a regional/foreign language with no Hindi/English equivalent.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 9(4)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-018-2",
        "field_name": "SALE_ABOVE_MRP",
        "requirement_type": "prohibition",
        "requirement": "No retail dealer or other person (including manufacturer, packer, importer, wholesale dealer) shall sell a packaged commodity at a price exceeding the declared retail sale price.",
        "severity": "critical",
        "explanation": "Distinct from label-declaration checks: this is a point-of-sale price-charged-vs-price-declared comparison, relevant if the system is extended to billing data.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 18(2)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-026-EXEMPT",
        "field_name": "SMALL_PACKAGE_EXEMPTION",
        "requirement_type": "conditional_exemption",
        "requirement": "Chapter II declarations (Rules 6-18) do not apply where net weight/measure is 10g/10ml or less; provided that packages of 10g-20g or 10ml-20ml must still declare MRP and net quantity. Also exempt: fast-food packed by restaurants/hotels, certain Drugs (Price Control) Order formulations, and agricultural produce above 50kg.",
        "severity": "medium",
        "explanation": "Prevents false-positive violations on very small sachets/samples that are lawfully exempt.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 26(a)-(d)",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-003-SCOPE",
        "field_name": "CHAPTER_II_APPLICABILITY",
        "requirement_type": "scope_limit",
        "requirement": "Chapter II (retail package declarations) does NOT apply to: (a) packages containing more than 25kg or 25 litre (except cement/fertilizer sold in bags up to 50kg, which ARE covered); (b) packages meant for industrial or institutional consumers.",
        "severity": "medium",
        "explanation": "Gate-check before applying any Rule 6 validation -- large/bulk and B2B packages are out of scope for this system's retail-focused checks.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 3(a)-(b) and Explanation thereto",
        "effective_from": "2011-04-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-10-ECOM-V1",
        "field_name": "ECOMMERCE_LISTING_DECLARATIONS",
        "requirement_type": "mandatory_declaration",
        "requirement": "Every e-commerce entity offering a pre-packaged commodity for sale must display, on the digital/electronic listing, all Rule 6(1) declarations applicable to that commodity EXCEPT the month/year of manufacture or packing.",
        "severity": "high",
        "explanation": "Extends label-based checks to online product listings, not just physical packages -- matches the pitch's 'e-commerce' scanning scope.",
        "source_reference": "Legal Metrology (Packaged Commodities) Rules, 2011 -- Rule 6(10), inserted by the Legal Metrology (Packaged Commodities) Amendment Rules, 2017 (Notification GSR 629(E) dated 23-06-2017)",
        "effective_from": "2018-01-01",
        "effective_to": None,
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-10A-COO-2026",
        "field_name": "ECOMMERCE_COUNTRY_OF_ORIGIN_FILTER",
        "requirement_type": "mandatory_declaration",
        "requirement": "Every e-commerce entity offering an imported product for sale must ensure the product listing contains a searchable and sortable filter specifying the country of origin.",
        "severity": "medium",
        "explanation": "Currently-active version of the country-of-origin filter mandate for imported goods sold online.",
        "source_reference": "Legal Metrology (Packaged Commodities) Amendment Rules, 2026 (Notification GSR 128(E) dated 13-02-2026), inserting Rule 6(10A)",
        "effective_from": "2026-07-01",
        "effective_to": "2027-06-30",
        "version": "1",
        "active": True,
    },
    {
        "rule_id": "LM-PC-006-10A-COO-2027",
        "field_name": "ECOMMERCE_COUNTRY_OF_ORIGIN_FILTER",
        "requirement_type": "mandatory_declaration",
        "requirement": "Every e-commerce entity offering an imported product for sale shall, with effect from 1 July 2027, ensure that the product listing of such imported product contains a searchable and sortable filter specifying the country of origin.",
        "severity": "medium",
        "explanation": "Future/not-yet-active replacement text for the same requirement; keep both rows so the engine can switch versions automatically on the effective date without a redeploy.",
        "source_reference": "Legal Metrology (Packaged Commodities) Second Amendment Rules, 2026 (Notification GSR 312(E) dated 27-04-2026), substituting Rule 6(10A)",
        "effective_from": "2027-07-01",
        "effective_to": None,
        "version": "2",
        "active": False,
    },
]


def _parse_date(date_str: str | None) -> datetime | None:
    if date_str is None:
        return None
    return datetime.strptime(date_str, "%Y-%m-%d")


def seed_rules() -> int:
    """Insert Member 2's 14 rules. Skips any rule_id that already exists.

    Returns the number of newly inserted rows.
    """
    create_tables()
    db = SessionLocal()
    inserted = 0
    try:
        existing_ids = {
            row[0]
            for row in db.query(Rule.rule_id).all()
        }
        for rule_data in RULES:
            if rule_data["rule_id"] in existing_ids:
                continue
            db.add(Rule(
                rule_id=rule_data["rule_id"],
                field_name=rule_data["field_name"],
                requirement_type=rule_data["requirement_type"],
                requirement=rule_data["requirement"],
                severity=rule_data["severity"],
                explanation=rule_data["explanation"],
                source_reference=rule_data["source_reference"],
                effective_from=_parse_date(rule_data["effective_from"]),
                effective_to=_parse_date(rule_data["effective_to"]),
                version=rule_data["version"],
                active=rule_data["active"],
            ))
            inserted += 1
        db.commit()
    finally:
        db.close()
    return inserted


def main():
    inserted = seed_rules()
    total = 0
    db = SessionLocal()
    try:
        total = db.query(Rule).count()
    finally:
        db.close()
    print(f"Inserted {inserted} new rule(s). Total rules in database: {total}")


if __name__ == "__main__":
    main()
