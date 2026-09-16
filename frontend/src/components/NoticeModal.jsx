import React, { useState } from 'react';
import { X, Printer, CheckCircle, FileText } from 'lucide-react';
import { OFFICER_PROFILE } from '../mockData';

export default function NoticeModal({ inspection, violations, onClose }) {
  const [isSigned, setIsSigned] = useState(false);
  const [signProgress, setSignProgress] = useState(false);

  if (!inspection) return null;

  const handleSign = () => {
    setSignProgress(true);
    setTimeout(() => {
      setSignProgress(false);
      setIsSigned(true);
    }, 600);
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-brand-navy/75 backdrop-blur-xs flex items-center justify-center p-3 sm:p-6">
      <div className="bg-white rounded-md shadow-xl border border-brand-sage w-full max-w-4xl overflow-hidden my-auto">
        {/* Top bar: bg-brand-navy */}
        <div className="bg-brand-navy text-white px-5 py-3.5 flex justify-between items-center border-b border-[#061a2e]">
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-brand-cream" />
            <span className="text-sm font-bold tracking-wide text-brand-cream">
              Official Statutory Notice Generator &bull; Section 32 & 39
            </span>
          </div>
          <button
            onClick={onClose}
            className="text-slate-300 hover:text-white p-1 rounded hover:bg-[#061a2e]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Printable Notice Content */}
        <div className="p-6 sm:p-10 max-h-[75vh] overflow-y-auto font-serif text-slate-900 bg-white">
          {/* Government Header */}
          <div className="text-center pb-6 border-b-2 border-brand-navy space-y-1">
            <div className="text-xs font-sans font-bold uppercase tracking-widest text-slate-600">
              GOVERNMENT OF NATIONAL CAPITAL TERRITORY OF DELHI
            </div>
            <h2 className="text-lg sm:text-xl font-bold uppercase tracking-tight text-brand-navy">
              OFFICE OF THE CONTROLLER OF LEGAL METROLOGY
            </h2>
            <p className="text-xs font-sans text-slate-600">
              Department of Consumer Affairs, Legal Metrology Complex, Vikas Bhawan, New Delhi - 110002
            </p>
            <div className="inline-block mt-2 px-3 py-1 bg-brand-cream/40 border border-brand-sage text-xs font-sans font-bold uppercase tracking-wider font-mono text-brand-navy">
              FORM - LM / VIO / NOTICE-2026
            </div>
          </div>

          {/* Reference & Date */}
          <div className="flex justify-between items-center text-xs font-sans py-4 border-b border-brand-sage/60">
            <div>
              <span className="font-bold text-brand-navy">Notice Ref. No.:</span>{' '}
              <span className="font-mono text-slate-800 font-bold">DLM/ND/2026/{inspection.id}</span>
            </div>
            <div>
              <span className="font-bold text-brand-navy">Date of Inspection:</span>{' '}
              <span>11 September 2026</span>
            </div>
          </div>

          {/* Recipient */}
          <div className="py-4 space-y-1 text-xs font-sans leading-relaxed">
            <p className="font-bold uppercase text-brand-navy">TO:</p>
            <p className="font-bold">{inspection.storeDetails?.name || 'The Occupier / Dealer'}</p>
            <p>Proprietor: {inspection.storeDetails?.proprietor || 'Shri Rameshwar Gupta'}</p>
            <p>{inspection.storeDetails?.address || 'Shop No. 14, Central Market, Kamla Nagar, Delhi - 110007'}</p>
            <p>License / Reg. No.: {inspection.storeDetails?.licenseNo || 'LMO-RETAIL-DEL-98442'}</p>
          </div>

          {/* Notice Subject */}
          <div className="py-3 px-4 bg-brand-cream/25 border-l-4 border-brand-navy font-sans text-xs space-y-1">
            <p className="font-bold uppercase tracking-wide text-brand-navy">
              SUBJECT: NOTICE UNDER SECTION 32 & 39 OF THE LEGAL METROLOGY ACT, 2009 READ WITH RULE 6 & 9 OF THE LEGAL METROLOGY (PACKAGED COMMODITIES) RULES, 2011.
            </p>
          </div>

          {/* Notice Body */}
          <div className="py-4 space-y-3 text-xs font-serif leading-relaxed text-slate-800">
            <p>
              WHEREAS, on routine regulatory market surveillance conducted by the undersigned Legal Metrology Officer at your premises on <strong>11/09/2026</strong>, pre-packaged commodities bearing brand <strong>"{inspection.productName}"</strong> (Batch No: <strong>{inspection.batchNo}</strong>) were examined through the automated compliance verification terminal (NiyamDrishti AI).
            </p>

            <p>
              WHEREAS, optical scan and physical verification established prima facie statutory contraventions under the Legal Metrology (Packaged Commodities) Rules, 2011:
            </p>

            {/* Violation List */}
            <div className="space-y-2 my-2 font-sans">
              {violations.map((v, idx) => (
                <div key={v.id} className="p-3 bg-red-50 border border-red-200 rounded-md text-xs">
                  <div className="flex items-center gap-2 font-bold text-red-900">
                    <span className="w-4 h-4 rounded bg-red-700 text-white flex items-center justify-center text-[10px]">
                      {idx + 1}
                    </span>
                    <span>{v.title} &mdash; Contravention of {v.ruleCitation}</span>
                  </div>
                  <p className="text-slate-700 mt-1 pl-6">
                    <span className="font-semibold">Defect noted:</span> {v.aiReasoning}
                  </p>
                  <p className="text-slate-600 mt-0.5 pl-6 font-mono text-[11px]">
                    On package: "{v.extractedText}" vs Required: "{v.expectedFormat}"
                  </p>
                </div>
              ))}
            </div>

            <p>
              NOW THEREFORE, take notice that you are required to submit your explanation in writing to the undersigned within <strong>seven (7) days</strong> from the date of receipt of this notice, showing cause why prosecution proceedings under Section 36(1) of the Legal Metrology Act, 2009 should not be instituted.
            </p>
          </div>

          {/* Signature Block */}
          <div className="mt-8 pt-4 border-t border-brand-sage flex justify-between items-end font-sans">
            <div className="text-xs text-slate-500 space-y-1 font-mono">
              <p>Place: North Delhi Circle 04</p>
              <p>GPS Verification: {inspection.storeDetails?.geoCoords || '28.6824° N, 77.2065° E'}</p>
              <div className="text-[10px] text-slate-400">
                Verification Hash: SHA256-4c9f-88a2-e01b
              </div>
            </div>

            <div className="text-right space-y-2">
              {isSigned ? (
                <div className="inline-block p-2 bg-emerald-50 border border-emerald-300 rounded-md text-left">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-emerald-800">
                    <CheckCircle className="w-4 h-4 text-emerald-700" />
                    <span>Digitally Signed & Validated</span>
                  </div>
                  <div className="text-[10px] font-mono text-emerald-700">
                    {OFFICER_PROFILE.name} ({OFFICER_PROFILE.badgeId})
                  </div>
                  <div className="text-[9px] text-slate-500 font-mono">
                    Timestamp: {new Date().toLocaleTimeString()} IST
                  </div>
                </div>
              ) : (
                <button
                  onClick={handleSign}
                  disabled={signProgress}
                  className="px-3 py-1.5 bg-brand-navy hover:bg-[#061a2e] text-white font-semibold text-xs rounded-md shadow-sm transition-colors"
                >
                  {signProgress ? 'Applying Digital Seal...' : 'Sign with Officer Token'}
                </button>
              )}
              <div className="text-xs font-bold text-brand-navy">{OFFICER_PROFILE.name}</div>
              <div className="text-[11px] text-slate-600">{OFFICER_PROFILE.designation}</div>
              <div className="text-[10px] text-slate-500">{OFFICER_PROFILE.zone}</div>
            </div>
          </div>
        </div>

        {/* Modal Footer Controls */}
        <div className="bg-slate-50 px-5 py-3 border-t border-brand-sage flex justify-between items-center">
          <span className="text-xs text-slate-600 font-sans">
            Statutory Notice &bull; Legal Metrology Act, 2009
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => window.print()}
              className="px-3.5 py-1.5 text-xs font-semibold bg-white text-brand-navy border border-brand-sage rounded-md hover:bg-slate-50 flex items-center gap-1.5 shadow-sm"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print Notice</span>
            </button>
            <button
              onClick={onClose}
              className="px-4 py-1.5 text-xs font-semibold bg-brand-navy text-white rounded-md hover:bg-[#061a2e] transition-colors shadow-sm"
            >
              Done
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
