import React from 'react';
import { 
  X, 
  Scale, 
  CheckCircle2, 
  AlertOctagon, 
  AlertTriangle, 
  Eye, 
  BookOpen,
  Info
} from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function EvidenceModal({ declaration, onClose, onOverrideStatus }) {
  if (!declaration) return null;

  const isViolation = declaration.status === 'violation';
  const isReview = declaration.status === 'review';

  const renderVisualEvidenceCrop = () => {
    if (declaration.id === 'mrp') {
      return (
        <div className="relative w-full h-64 bg-slate-950 rounded-md overflow-hidden border border-brand-navy flex flex-col justify-center items-center select-none">
          <div className="absolute inset-0 bg-slate-900 opacity-95"></div>
          
          <div className="relative z-10 w-4/5 bg-white text-slate-900 p-4 rounded border border-brand-sage font-sans shadow-sm">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest border-b border-brand-sage/60 pb-1 flex justify-between font-mono">
              <span>B.NO: SB-2026-B09</span>
              <span>MFD: 08/2026</span>
            </div>

            <div className="my-3 p-2.5 border-2 border-red-600 bg-red-50 rounded">
              <div className="flex justify-between items-center mb-1">
                <span className="bg-red-700 text-white text-[10px] font-mono font-bold px-1.5 py-0.5 rounded">
                  OCR REGION [98.2% CONF]
                </span>
                <span className="text-[10px] font-mono text-slate-500">RULE 6(1)(e)</span>
              </div>
              <p className="text-base font-bold text-slate-900 font-mono tracking-wide">
                MRP Rs 45/- only
              </p>
              <p className="text-xs text-red-700 font-bold mt-1 flex items-center gap-1">
                <AlertOctagon className="w-3.5 h-3.5 flex-shrink-0" />
                MISSING STATUTORY TEXT: "(inclusive of all taxes)"
              </p>
            </div>

            <div className="text-[10px] text-slate-600 font-mono flex justify-between">
              <span>USE BY: 6 MONTHS</span>
              <span>NET WT: 200 g</span>
            </div>
          </div>

          <div className="absolute bottom-2 left-3 right-3 bg-[#061a2e] text-brand-cream px-3 py-1.5 rounded text-[11px] flex justify-between items-center border border-brand-sage/40 font-mono">
            <span className="text-brand-cream">Coord: [x:142, y:88, w:320, h:65]</span>
            <span className="text-emerald-400 font-bold">Contrast 14.2:1 (PASS)</span>
          </div>
        </div>
      );
    }

    if (declaration.id === 'readability') {
      return (
        <div className="relative w-full h-64 bg-slate-950 rounded-md overflow-hidden border border-brand-navy flex flex-col justify-center items-center select-none">
          <div className="relative z-10 w-4/5 bg-white text-slate-900 p-4 rounded border border-brand-sage shadow-sm">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest border-b border-brand-sage/60 pb-1 font-mono">
              RULE 9 - NUMERAL HEIGHT INSPECTION
            </div>

            <div className="my-3 p-3 border-2 border-amber-600 bg-amber-50 rounded">
              <div className="flex justify-between items-center mb-1">
                <span className="bg-amber-700 text-white text-[10px] font-mono font-bold px-1.5 py-0.5 rounded">
                  Digital Caliper Gauge
                </span>
                <span className="text-[10px] font-mono text-slate-600">Table 1 Standards</span>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <span className="text-xs text-slate-500 uppercase">Target Numeral:</span>
                  <div className="text-base font-black font-mono text-slate-900">
                    Net Wt: <span className="underline decoration-amber-600 decoration-2">200</span> g
                  </div>
                </div>

                <div className="text-right border-l-2 border-amber-500 pl-3">
                  <div className="text-xs text-slate-500">Vision Measured:</div>
                  <div className="text-base font-bold text-amber-800 font-mono">1.85 mm</div>
                  <div className="text-[10px] text-slate-700 font-bold">Legal Minimum: 3.00 mm</div>
                </div>
              </div>

              <div className="mt-2.5 pt-2 border-t border-amber-200">
                <div className="w-full bg-slate-200 h-2 rounded overflow-hidden flex">
                  <div className="bg-amber-600 h-full w-[61%]"></div>
                  <div className="bg-red-500 h-full w-[39%]"></div>
                </div>
                <div className="flex justify-between text-[10px] text-slate-600 font-mono mt-1">
                  <span>0 mm</span>
                  <span className="text-amber-800 font-bold">1.85 mm (Measured)</span>
                  <span className="text-slate-900 font-bold">3.00 mm (Statutory)</span>
                </div>
              </div>
            </div>

            <p className="text-[11px] text-slate-600 font-medium">
              Display Area: 185 cm² &rarr; PCR 2011 Table 1 requires minimum 3.0 mm height.
            </p>
          </div>
        </div>
      );
    }

    if (declaration.id === 'consumer_care') {
      return (
        <div className="relative w-full h-64 bg-slate-950 rounded-md overflow-hidden border border-brand-navy flex flex-col justify-center items-center select-none">
          <div className="relative z-10 w-4/5 bg-white text-slate-900 p-4 rounded border border-brand-sage shadow-sm">
            <div className="text-[10px] text-slate-500 uppercase tracking-widest border-b border-brand-sage/60 pb-1 font-mono">
              RULE 6(1)(da) CONTACT VERIFICATION
            </div>

            <div className="my-3 p-3 border-2 border-red-600 bg-red-50 rounded space-y-1 font-mono text-xs">
              <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                <span>Email: care@sunburstbiscuits.com (FOUND)</span>
              </div>
              <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
                <span>Postal Address: Factory premise listed (FOUND)</span>
              </div>
              <div className="flex items-center gap-2 text-red-800 font-bold bg-red-100 p-1 rounded border border-red-200">
                <AlertOctagon className="w-3.5 h-3.5 text-red-700" />
                <span>Telephone / Helpline: [NOT DECLARED ON PACKAGING]</span>
              </div>
            </div>

            <p className="text-[11px] text-red-700 font-bold">
              * PCR 2011 mandates BOTH telephone number and email address.
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="relative w-full h-64 bg-slate-950 rounded-md overflow-hidden border border-brand-navy flex flex-col justify-center items-center select-none p-6">
        <div className="relative z-10 w-full max-w-md bg-slate-900 border border-brand-sage p-4 rounded-md text-slate-200">
          <div className="text-[10px] text-slate-400 uppercase font-mono pb-1 border-b border-brand-sage/60 flex justify-between">
            <span>OCR Extraction Region</span>
            <span className="text-emerald-400 font-bold">Confidence: {declaration.aiConfidence}%</span>
          </div>
          <div className="my-3 p-3 bg-slate-950 rounded border border-slate-800 font-mono text-sm text-slate-100">
            "{declaration.extractedText}"
          </div>
          <div className="text-xs text-slate-400 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>Target Pattern Validated against Schedule II</span>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-brand-navy/70 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6">
      <div className="bg-white rounded-md shadow-xl border border-brand-sage w-full max-w-3xl overflow-hidden my-auto">
        
        {/* Header: bg-brand-navy */}
        <div className="bg-brand-navy text-white px-5 py-3.5 flex items-center justify-between border-b border-[#061a2e]">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded bg-[#061a2e] text-brand-cream border border-brand-sage/40">
              <Scale className="w-5 h-5 text-brand-cream" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-bold text-white tracking-wide">
                  {declaration.title}
                </h3>
                <StatusBadge status={declaration.status} size="sm" />
              </div>
              <p className="text-xs text-brand-cream font-mono font-medium">
                {declaration.ruleCitation}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-300 hover:text-white p-1 rounded hover:bg-[#061a2e] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-5 sm:p-6 space-y-5 max-h-[75vh] overflow-y-auto text-brand-navy">
          
          {/* Visual Evidence Section */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-xs font-bold text-brand-navy uppercase tracking-wider flex items-center gap-1.5">
                <Eye className="w-4 h-4 text-brand-navy" />
                Optical Character Recognition & Visual Crop Evidence
              </h4>
              <span className="text-[11px] font-mono text-slate-500">
                {declaration.evidence?.cropTitle || 'Optical Evidence Panel'}
              </span>
            </div>
            
            {renderVisualEvidenceCrop()}
          </div>

          {/* Legal Rule Comparison Table */}
          <div className="border border-brand-sage rounded-md overflow-hidden">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-brand-cream/30 text-brand-navy font-bold border-b border-brand-sage">
                  <th className="p-3 w-1/3">Statutory Legal Standard</th>
                  <th className="p-3 w-1/3">Verbatim OCR Extracted Text</th>
                  <th className="p-3 w-1/3">Assessment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-sage/40 font-sans">
                <tr className="align-top">
                  <td className="p-3 bg-slate-50 text-slate-700 leading-relaxed font-medium">
                    {declaration.statutoryRequirement}
                  </td>
                  <td className="p-3 font-mono text-brand-navy font-bold bg-white">
                    "{declaration.extractedText}"
                  </td>
                  <td className="p-3">
                    {isViolation && (
                      <div className="text-red-800 font-bold flex items-start gap-1.5">
                        <AlertOctagon className="w-4 h-4 text-red-700 flex-shrink-0 mt-0.5" />
                        <span>Non-Compliant: Mandatory term missing</span>
                      </div>
                    )}
                    {isReview && (
                      <div className="text-amber-800 font-bold flex items-start gap-1.5">
                        <AlertTriangle className="w-4 h-4 text-amber-700 flex-shrink-0 mt-0.5" />
                        <span>Review: Dimension requires caliper check</span>
                      </div>
                    )}
                    {!isViolation && !isReview && (
                      <div className="text-emerald-800 font-bold flex items-start gap-1.5">
                        <CheckCircle2 className="w-4 h-4 text-emerald-700 flex-shrink-0 mt-0.5" />
                        <span>Rule Fully Satisfied</span>
                      </div>
                    )}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* AI Advisory Reasoning */}
          <div className="bg-slate-50 border-l-4 border-l-brand-navy border border-brand-sage p-4 rounded-r-md space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-brand-navy uppercase tracking-wider flex items-center gap-1.5">
                <BookOpen className="w-3.5 h-3.5 text-brand-navy" />
                AI Assistant Legal Finding
              </span>
              <span className="text-xs font-mono font-bold text-brand-navy bg-brand-cream/40 border border-brand-sage px-2 py-0.5 rounded">
                Confidence: {declaration.aiConfidence}%
              </span>
            </div>
            <p className="text-xs text-slate-700 leading-relaxed">
              {declaration.aiReasoning}
            </p>
            {declaration.penaltySection && (
              <p className="text-[11px] text-slate-600 font-medium pt-1 border-t border-brand-sage/60">
                <strong className="text-brand-navy">Statutory Provision:</strong> {declaration.penaltySection}
              </p>
            )}
          </div>

          {/* Legal Defensibility Disclaimer */}
          <div className="flex items-start gap-2 text-[11px] text-slate-600 bg-brand-cream/30 p-3 rounded-md border border-brand-sage">
            <Info className="w-4 h-4 text-brand-navy flex-shrink-0 mt-0.5" />
            <p>
              <strong>Official Notice:</strong> The AI model functions solely as an investigative aid. The Legal Metrology Officer retains final statutory power to accept or override this finding.
            </p>
          </div>
        </div>

        {/* Modal Footer / Inspector Action */}
        <div className="bg-slate-50 px-5 py-3 border-t border-brand-sage flex flex-wrap items-center justify-between gap-3">
          <div className="text-xs font-semibold text-brand-navy">
            Officer Override:
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                onOverrideStatus(declaration.id, 'compliant');
                onClose();
              }}
              className="px-3 py-1.5 text-xs font-bold text-emerald-800 bg-emerald-100 hover:bg-emerald-200 border border-emerald-300 rounded-md transition-colors"
            >
              Mark Compliant
            </button>
            <button
              onClick={() => {
                onOverrideStatus(declaration.id, 'violation');
                onClose();
              }}
              className="px-3 py-1.5 text-xs font-bold text-red-800 bg-red-100 hover:bg-red-200 border border-red-300 rounded-md transition-colors"
            >
              Confirm Violation
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 text-xs font-bold text-white bg-brand-navy hover:bg-[#061a2e] rounded-md transition-colors"
            >
              Close
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
