import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-brand-navy text-slate-300 text-xs border-t border-[#061a2e] mt-12 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4">
        
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-[#061a2e] text-brand-cream border border-brand-sage/40 flex items-center justify-center shadow-sm">
            <ShieldCheck className="w-4 h-4 text-brand-cream" />
          </div>
          <div>
            <span className="font-bold text-white">NiyamDrishti AI</span> &bull;{' '}
            <span className="text-brand-cream">Smart India Hackathon (SIH) Prototype</span>
          </div>
        </div>

        <div className="text-center md:text-right text-[11px] text-slate-300">
          <p>
            Regulatory Enforcement System for Legal Metrology (Packaged Commodities) Rules, 2011.
          </p>
          <p className="text-slate-400 mt-0.5">
            Designed for Department of Consumer Affairs &bull; Field Officer Assistance Portal
          </p>
        </div>

      </div>
    </footer>
  );
}
