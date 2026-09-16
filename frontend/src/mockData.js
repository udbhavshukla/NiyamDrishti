// Legal Metrology (Packaged Commodities) Rules, 2011 Compliance Mock Dataset
// High-stakes Hackathon Prototype for Smart India Hackathon (SIH)

export const OFFICER_PROFILE = {
  name: "Rajesh Sharma",
  designation: "Legal Metrology Officer (LMO)",
  badgeId: "LMO-DEL-2024-884",
  zone: "North Delhi District - Circle 04",
  station: "Directorate of Legal Metrology, Delhi HQ",
  avatarUrl: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80",
  activeInspectionsToday: 14,
  violationsDetectedToday: 3,
};

export const RECENT_SCANS = [
  {
    id: "INSP-2026-DEL-0492",
    productName: "Sunburst Choco Delite Biscuits",
    variant: "200g Standard Pack",
    category: "Bakery & Confectionery",
    gtin: "8901234567890",
    storeName: "M/s Gupta General Stores & Supermarket",
    storeAddress: "Shop 14, Main Market, Kamla Nagar, Delhi - 110007",
    inspectedAt: "Today, 11:42 AM",
    timestamp: "2026-09-11T11:42:00Z",
    overallStatus: "violation", // 'violation' | 'review' | 'compliant'
    overallConfidence: 95.8,
    violationCount: 2,
    reviewCount: 1,
    compliantCount: 4,
    thumbnail: "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=300&auto=format&fit=crop&q=80"
  },
  {
    id: "INSP-2026-DEL-0491",
    productName: "Pavitra Gold Refined Mustard Oil",
    variant: "1 Litre Pouch",
    category: "Edible Oils & Fats",
    gtin: "8909876543211",
    storeName: "Reliance Smart Point",
    storeAddress: "Plot 8, Block B, Model Town, Delhi - 110009",
    inspectedAt: "Today, 10:15 AM",
    timestamp: "2026-09-11T10:15:00Z",
    overallStatus: "review",
    overallConfidence: 91.2,
    violationCount: 0,
    reviewCount: 2,
    compliantCount: 5,
    thumbnail: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=300&auto=format&fit=crop&q=80"
  },
  {
    id: "INSP-2026-DEL-0490",
    productName: "Kohinoor Royal Basmati Rice",
    variant: "5 kg Poly Bag",
    category: "Food Grains & Pulses",
    gtin: "8904567891234",
    storeName: "Aggarwal Wholesale Mart",
    storeAddress: "B-22, Azadpur Mandi Sub-Yard, Delhi - 110033",
    inspectedAt: "Yesterday, 04:30 PM",
    timestamp: "2026-09-10T16:30:00Z",
    overallStatus: "compliant",
    overallConfidence: 98.4,
    violationCount: 0,
    reviewCount: 0,
    compliantCount: 7,
    thumbnail: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=300&auto=format&fit=crop&q=80"
  },
  {
    id: "INSP-2026-DEL-0489",
    productName: "Apex Hydro Fuel Energy Drink",
    variant: "250 ml Aluminium Can",
    category: "Imported Beverages",
    gtin: "9312345678902",
    storeName: "Modern Bazaar Select",
    storeAddress: "Ground Floor, City Centre Mall, Rohini, Delhi - 110085",
    inspectedAt: "Yesterday, 02:10 PM",
    timestamp: "2026-09-10T14:10:00Z",
    overallStatus: "violation",
    overallConfidence: 97.1,
    violationCount: 2,
    reviewCount: 1,
    compliantCount: 4,
    thumbnail: "https://images.unsplash.com/photo-1622543925917-763c34d1a86e?w=300&auto=format&fit=crop&q=80"
  }
];

export const MOCK_INSPECTION_DETAIL = {
  id: "INSP-2026-DEL-0492",
  productName: "Sunburst Choco Delite Biscuits",
  brand: "Sunburst Confectionery Ltd.",
  category: "Bakery / Pre-Packaged Snacks",
  batchNo: "SB-2026-BATCH09",
  dateOfManufacture: "08/2026",
  bestBefore: "6 Months from Mfd",
  principalDisplayArea: "185 sq. cm",
  mandatoryNumeralHeightRequired: "3.0 mm",
  storeDetails: {
    name: "M/s Gupta General Stores & Supermarket",
    proprietor: "Shri Rameshwar Gupta",
    licenseNo: "LMO-RETAIL-DEL-98442",
    address: "Shop No. 14, Central Market, Kamla Nagar, North Delhi - 110007",
    geoCoords: "28.6824° N, 77.2065° E"
  },
  scanMeta: {
    scannedAt: "11 September 2026, 11:42:15 IST",
    device: "Samsung Galaxy XCover Pro (Govt Issued Rugged Terminal)",
    ocrEngine: "NiyamDrishti LegalOCR v2.4 (Transformer LayoutLMv3 + Rule Engine)",
    overallStatus: "violation", // 'violation' | 'review' | 'compliant'
    overallConfidence: 95.8,
    statusSummary: "2 Critical Legal Violations & 1 Review Required detected under Rules 6 & 9 of Legal Metrology (Packaged Commodities) Rules, 2011."
  },
  packageImages: {
    front: "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600&auto=format&fit=crop&q=80",
    back: "https://images.unsplash.com/photo-1590080875515-8a3a8dc5735e?w=600&auto=format&fit=crop&q=80",
    mrpPanel: "https://images.unsplash.com/photo-1589758438368-0ad531db3366?w=600&auto=format&fit=crop&q=80",
    barcode: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=600&auto=format&fit=crop&q=80"
  },
  declarations: [
    {
      id: "mrp",
      ruleCitation: "Rule 6(1)(e) - Maximum Retail Price",
      title: "Maximum Retail Price (MRP) & Tax Inclusivity",
      statutoryRequirement: "Must state 'Maximum Retail Price ₹ xx.xx (inclusive of all taxes)' or 'MRP Rs. xx (incl. of all taxes)'. Mandatory wordings must not be omitted.",
      status: "violation", // 'violation' | 'review' | 'compliant'
      aiConfidence: 98.2,
      extractedText: "MRP Rs 45/- only",
      expectedFormat: "MRP Rs. 45.00 (incl. of all taxes)",
      aiReasoning: "CRITICAL VIOLATION: Omission of mandatory statutory declaration '(inclusive of all taxes)' or '(incl. of all taxes)'. Omitting tax inclusivity violates Section 18 of LM Act, 2009 read with Rule 6(1)(e) of PCR 2011.",
      penaltySection: "Compoundable offence under Rule 32(1) punishable with fine up to ₹25,000 for first violation.",
      evidence: {
        cropTitle: "Macro Crop: Price Panel (Back Top-Right)",
        labelSnippet: "MRP Rs 45/- only",
        defectDetected: "Missing '(inclusive of all taxes)' suffix",
        boundingBox: { top: "28%", left: "62%", width: "32%", height: "18%" },
        ocrRaw: "BATCH: SB-2026-B09\nMFD: 08/2026\nMRP Rs 45/- only\nUSE BY: 6 MONTHS",
        rulerMetric: "Contrast Ratio: 14.2:1 (Sufficient) | Tax phrase: 0% match"
      }
    },
    {
      id: "consumer_care",
      ruleCitation: "Rule 6(1)(da) - Consumer Grievance Redressal",
      title: "Consumer Care Contact Details",
      statutoryRequirement: "Must declare Name, Address, Telephone Number, and Email Address of the designated consumer grievance officer / consumer cell.",
      status: "violation",
      aiConfidence: 96.5,
      extractedText: "For feedback: write to care@sunburstbiscuits.com or postal address given above.",
      expectedFormat: "Consumer Care Officer: Name/Dept, Full Postal Address, Working Telephone/Toll-Free No., Email ID",
      aiReasoning: "STATUTORY DEFECT: Mandatory Telephone / Helpline number is completely missing from the consumer care panel. Under Rule 6(1)(da), providing an email alone is insufficient.",
      penaltySection: "Notice under Rule 32 of Legal Metrology (Packaged Commodities) Rules, 2011.",
      evidence: {
        cropTitle: "Macro Crop: Consumer Relations Block (Side Panel)",
        labelSnippet: "For feedback: write to care@sunburstbiscuits.com",
        defectDetected: "Missing mandatory Telephone/Helpline number",
        boundingBox: { top: "64%", left: "10%", width: "80%", height: "24%" },
        ocrRaw: "CONSUMER CARE CELL:\nSunburst Confectionery Ltd.\nEmail: care@sunburstbiscuits.com\nWeb: www.sunburstbiscuits.com\n[TEL NO NOT DETECTED]",
        rulerMetric: "Missing Field: Telephone / Mobile Number"
      }
    },
    {
      id: "readability",
      ruleCitation: "Rule 9(1) & Table 1 - Numeral & Letter Height",
      title: "Declaration Readability & Font Size Standards",
      statutoryRequirement: "For Principal Display Panel area between 100 cm² and 500 cm², minimum numeral height for Net Quantity must be at least 3.0 mm.",
      status: "review",
      aiConfidence: 87.4,
      extractedText: "Net Wt: 200 g (Measured numeral height: ~1.85 mm)",
      expectedFormat: "Numeral '200' height >= 3.0 mm for package display area 185 cm²",
      aiReasoning: "BORDERLINE / POTENTIAL VIOLATION: Computer vision edge measurement detects Net Quantity numeral height of approximately 1.85 mm. Required statutory minimum under Table 1 is 3.0 mm. Inspector physical caliper verification strongly advised.",
      penaltySection: "Section 39 / Rule 9(1) Defective Display Declaration.",
      evidence: {
        cropTitle: "Visual Caliper Overlay: Net Qty Height Analysis",
        labelSnippet: "Net Wt: 200 g (Height: 1.85 mm)",
        defectDetected: "Numeral height 1.85 mm < Statutory minimum 3.0 mm",
        boundingBox: { top: "72%", left: "54%", width: "38%", height: "20%" },
        ocrRaw: "Net Wt: 200 g\n(approx. 24 biscuits)\nDetected Height: 1.85mm\nTarget: 3.00mm",
        rulerMetric: "Scale: 1.85mm measured vs 3.00mm legal standard (38% deficiency)"
      }
    },
    {
      id: "net_qty",
      ruleCitation: "Rule 6(1)(f) & Schedule II - Standard Net Quantity",
      title: "Net Quantity Declaration & Standard Unit",
      statutoryRequirement: "Must state standard metric units (g, kg, ml, l). Must NOT include misleading qualifying terms such as 'Jumbo', 'Extra', 'When Packed', or 'Approximate'.",
      status: "compliant",
      aiConfidence: 99.1,
      extractedText: "Net Quantity: 200 g",
      expectedFormat: "Standard unit 'g' declared without unauthorized qualifiers",
      aiReasoning: "FULL COMPLIANCE: Standard unit 'g' correctly specified. No impermissible qualifying prefixes or suffixes detected.",
      penaltySection: "N/A - Rule Satisfied",
      evidence: {
        cropTitle: "Macro Crop: Net Quantity Declaration",
        labelSnippet: "Net Quantity: 200 g",
        defectDetected: "None. Compliant declaration.",
        boundingBox: { top: "68%", left: "50%", width: "42%", height: "16%" },
        ocrRaw: "Net Quantity: 200 g\nValid unit: gram (g)",
        rulerMetric: "Metric Unit: 'g' - Validated against Schedule II"
      }
    },
    {
      id: "mfg_address",
      ruleCitation: "Rule 6(1)(a) - Manufacturer & Packer Address",
      title: "Manufacturer / Packer Full Postal Address",
      statutoryRequirement: "Must state complete address where the company is situated, including factory premise, city, pin code, and state.",
      status: "compliant",
      aiConfidence: 94.8,
      extractedText: "Manufactured & Packed by: Sunburst Confectionery Ltd., Plot No. 44-46, Industrial Area Phase II, Sonipat, Haryana - 131001, India.",
      expectedFormat: "Complete postal address including unit no., district, state, and valid 6-digit PIN code",
      aiReasoning: "FULL COMPLIANCE: Complete corporate and factory address verified. Valid Indian Postal PIN code (131001) parsed and geocoded successfully.",
      penaltySection: "N/A - Rule Satisfied",
      evidence: {
        cropTitle: "Macro Crop: Manufacturer Address Block",
        labelSnippet: "Sunburst Confectionery Ltd., Sonipat, Haryana - 131001",
        defectDetected: "None. All geographic components present.",
        boundingBox: { top: "40%", left: "8%", width: "84%", height: "22%" },
        ocrRaw: "Mfg & Pkd by:\nSunburst Confectionery Ltd.\nPlot 44-46, Ind Area Phase II\nSonipat, Haryana - 131001",
        rulerMetric: "Postal PIN: 131001 (Valid: Haryana Circle)"
      }
    },
    {
      id: "mfg_date",
      ruleCitation: "Rule 6(1)(d) - Date of Manufacture / Packaging",
      title: "Month & Year of Manufacture or Packaging",
      statutoryRequirement: "Must state month and year of manufacture (e.g. 08/2026 or Aug 2026) clearly and legibly.",
      status: "compliant",
      aiConfidence: 97.6,
      extractedText: "MFD: 08/2026 | BEST BEFORE: 6 MONTHS FROM PKG",
      expectedFormat: "Month and Year of manufacture or packing in standard notation",
      aiReasoning: "FULL COMPLIANCE: Standard numeric month/year format '08/2026' found on inkjet batch stamp. Fully legible.",
      penaltySection: "N/A - Rule Satisfied",
      evidence: {
        cropTitle: "Inkjet Stamp Crop: Batch & Date Panel",
        labelSnippet: "MFD: 08/2026",
        defectDetected: "None.",
        boundingBox: { top: "18%", left: "58%", width: "36%", height: "16%" },
        ocrRaw: "B.No: SB-2026-B09\nMFD: 08/2026\nEXP: 02/2027",
        rulerMetric: "OCR Confidence: 97.6%"
      }
    },
    {
      id: "country_of_origin",
      ruleCitation: "Rule 6(1)(b) - Country of Origin",
      title: "Country of Origin Declaration",
      statutoryRequirement: "Mandatory declaration of country where manufactured or imported from.",
      status: "compliant",
      aiConfidence: 99.4,
      extractedText: "Country of Origin: India / Made in India",
      expectedFormat: "'Country of Origin: India' or 'Made in India'",
      aiReasoning: "FULL COMPLIANCE: Unambiguous Country of Origin declaration detected on lower banner.",
      penaltySection: "N/A - Rule Satisfied",
      evidence: {
        cropTitle: "Macro Crop: Origin Indicator",
        labelSnippet: "Country of Origin: India",
        defectDetected: "None.",
        boundingBox: { top: "86%", left: "30%", width: "40%", height: "12%" },
        ocrRaw: "COUNTRY OF ORIGIN: INDIA\nProduct of India",
        rulerMetric: "Origin: India (Domestic product)"
      }
    }
  ]
};

// Alternative product scenarios to switch during demo
export const DEMO_PRESETS = [
  {
    id: "preset-biscuits",
    name: "Sunburst Choco Delite Biscuits (Violations Present)",
    category: "Packaged Snack / Biscuits",
    badge: "2 Violations",
    badgeColor: "violation",
    data: MOCK_INSPECTION_DETAIL
  },
  {
    id: "preset-oil",
    name: "Pavitra Gold Refined Mustard Oil (Review Needed)",
    category: "Edible Oils & Fats",
    badge: "2 Review Required",
    badgeColor: "review",
    data: {
      ...MOCK_INSPECTION_DETAIL,
      id: "INSP-2026-DEL-0491",
      productName: "Pavitra Gold Refined Mustard Oil",
      brand: "Pavitra Agro Foods Pvt. Ltd.",
      category: "Edible Oils & Fats",
      batchNo: "PG-OIL-882",
      packageImages: {
        front: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
        back: "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&auto=format&fit=crop&q=80",
        mrpPanel: "https://images.unsplash.com/photo-1589758438368-0ad531db3366?w=600&auto=format&fit=crop&q=80",
        barcode: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=600&auto=format&fit=crop&q=80"
      },
      scanMeta: {
        ...MOCK_INSPECTION_DETAIL.scanMeta,
        overallStatus: "review",
        overallConfidence: 91.2,
        statusSummary: "Review required on Net Quantity declaration under Schedule III (Volume vs Equivalent Mass declaration)."
      },
      declarations: MOCK_INSPECTION_DETAIL.declarations.map(d => {
        if (d.id === "mrp") {
          return {
            ...d,
            status: "compliant",
            extractedText: "MRP ₹ 145.00 (inclusive of all taxes)",
            aiReasoning: "FULL COMPLIANCE: Valid rupee symbol and explicit tax inclusion phrase verified.",
            evidence: { ...d.evidence, defectDetected: "None. Legitimate MRP statement." }
          };
        }
        if (d.id === "consumer_care") {
          return {
            ...d,
            status: "compliant",
            extractedText: "Helpline: 1800-200-9944, Email: care@pavitragold.com",
            aiReasoning: "FULL COMPLIANCE: Toll-free helpline, address, and email all present.",
            evidence: { ...d.evidence, defectDetected: "None." }
          };
        }
        if (d.id === "net_qty") {
          return {
            ...d,
            status: "review",
            extractedText: "Net Quantity: 1 Litre (Mass equivalent missing)",
            aiReasoning: "REVIEW REQUIRED: Under Second Amendment to PCR 2011, edible oils packed in volume (Litres) must also declare equivalent net quantity in mass (grams/kg).",
            evidence: {
              ...d.evidence,
              defectDetected: "Missing equivalent mass declaration (e.g. '1 L (910 g)')"
            }
          };
        }
        return d;
      })
    }
  },
  {
    id: "preset-rice",
    name: "Kohinoor Royal Basmati Rice (100% Compliant)",
    category: "Food Grains & Pulses",
    badge: "All Compliant",
    badgeColor: "compliant",
    data: {
      ...MOCK_INSPECTION_DETAIL,
      id: "INSP-2026-DEL-0490",
      productName: "Kohinoor Royal Basmati Rice",
      brand: "Kohinoor Speciality Foods India Pvt. Ltd.",
      category: "Food Grains & Pulses",
      batchNo: "KR-RICE-2026-X1",
      packageImages: {
        front: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        back: "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        mrpPanel: "https://images.unsplash.com/photo-1589758438368-0ad531db3366?w=600&auto=format&fit=crop&q=80",
        barcode: "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=600&auto=format&fit=crop&q=80"
      },
      scanMeta: {
        ...MOCK_INSPECTION_DETAIL.scanMeta,
        overallStatus: "compliant",
        overallConfidence: 98.4,
        statusSummary: "100% Compliant. All 7 mandatory statutory declarations strictly satisfy Legal Metrology Rules, 2011."
      },
      declarations: MOCK_INSPECTION_DETAIL.declarations.map(d => ({
        ...d,
        status: "compliant",
        aiReasoning: "FULL COMPLIANCE: Statutory requirements completely verified against PCR 2011 standard database.",
        evidence: {
          ...d.evidence,
          defectDetected: "None. All requirements satisfied."
        }
      }))
    }
  }
];
