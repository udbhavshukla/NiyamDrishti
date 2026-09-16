import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  AlertOctagon, 
  AlertTriangle, 
  CheckCircle2, 
  ArrowLeft, 
  Eye, 
  Check, 
  Store, 
  MapPin, 
  Calendar, 
  Scale, 
  FileText,
  Info
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import EvidenceModal from '../components/EvidenceModal';
import NoticeModal from '../components/NoticeModal';
import { MOCK_INSPECTION_DETAIL, OFFICER_PROFILE } from '../mockData';
import { submitReviewOverride } from '../api';

export default function ComplianceResult() {
  const location = useLocation();
  const navigate = useNavigate();

  const initialProduct = location.state?.productData || MOCK_INSPECTION_DETAIL;
  
  const [product, setProduct] = useState(initialProduct);
  const [selectedImageTab, setSelectedImageTab] = useState('back');
  const [activeEvidenceDeclaration, setActiveEvidenceDeclaration] = useState(null);
  const [showNoticeModal, setShowNoticeModal] = useState(false);
  const [inspectorNotes, setInspectorNotes] = useState('');
  const [isReportConfirmed, setIsReportConfirmed] = useState(false);

  // Inspector Overrides Map
  const [overrides, setOverrides] = useState({});

  const currentDeclarations = product.declarations.map((d) => ({
    ...d,
    currentStatus: overrides[d.id] || d.status,
  }));

  const violationCount = currentDeclarations.filter(d => d.currentStatus === 'violation').length;
  const reviewCount = currentDeclarations.filter(d => d.currentStatus === 'review').length;
  const compliantCount = currentDeclarations.filter(d => d.currentStatus === 'compliant' || d.currentStatus === 'waived').length;

  let overallStatus = 'compliant';
  if (violationCount > 0) {
    overallStatus = 'violation';
  } else if (reviewCount > 0) {
    overallStatus = 'review';
  }

  const handleOverride = (id, newStatus) => {
    setOverrides(prev => ({
      ...prev,
      [id]: newStatus
    }));
    const apiDecision = newStatus === 'compliant' ? 'PASS' : (newStatus === 'violation' ? 'FAIL' : 'REVIEW_REQUIRED');
    submitReviewOverride(product.id, apiDecision, `Inspector override on declaration ${id}: ${newStatus}`, OFFICER_PROFILE.badgeId);
  };

  const activeViolations = currentDeclarations.filter(d => d.currentStatus === 'violation');

  const bannerStyles = {
    violation: 'bg-white border border-brand-sage border-l-4 border-l-red-600',
    review: 'bg-white border border-brand-sage border-l-4 border-l-amber-500',
    compliant: 'bg-white border border-brand-sage border-l-4 border-l-emerald-600'
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Top Breadcrumb & Navigation */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={() => navigate('/inspector-home')}
          className="text-xs font-semibold text-brand-navy hover:text-black flex items-center gap-1.5 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Inspector Dashboard</span>
        </button>

        <div className="flex items-center gap-2">
          <span className="text-xs font-mono text-slate-500">Case ID:</span>
          <span className="text-xs font-mono font-bold bg-brand-cream/40 border border-brand-sage px-2 py-0.5 rounded text-brand-navy">
            {product.id}
          </span>
        </div>
      </div>

      {/* Authoritative Overall Status Banner with Crisp Left Accent */}
      <div className={`rounded-md p-5 sm:p-6 shadow-sm transition-all ${bannerStyles[overallStatus]}`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center gap-2.5">
              <StatusBadge status={overallStatus} size="banner" />
              <span className="text-xs font-mono font-bold text-brand-navy bg-brand-cream/30 px-2.5 py-1 rounded border border-brand-sage">
                Confidence: {product.scanMeta.overallConfidence}%
              </span>
              <span className="text-xs font-semibold text-slate-600 font-mono">
                PCR 2011 REGULATORY AUDIT
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-brand-navy mt-1">
              {product.productName}
            </h1>

            <p className="text-xs sm:text-sm text-slate-700 max-w-3xl">
              {product.scanMeta.statusSummary}
            </p>
          </div>

          {/* Quick Summary Counts */}
          <div className="flex items-center gap-2 sm:gap-3 bg-slate-50 p-3 rounded-md border border-brand-sage shadow-sm flex-shrink-0">
            <div className="text-center px-2">
              <span className="text-lg sm:text-xl font-black text-red-700 block">{violationCount}</span>
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Violations</span>
            </div>
            <div className="w-px h-8 bg-brand-sage"></div>
            <div className="text-center px-2">
              <span className="text-lg sm:text-xl font-black text-amber-700 block">{reviewCount}</span>
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Review</span>
            </div>
            <div className="w-px h-8 bg-brand-sage"></div>
            <div className="text-center px-2">
              <span className="text-lg sm:text-xl font-black text-emerald-700 block">{compliantCount}</span>
              <span className="text-[10px] font-bold text-slate-600 uppercase tracking-wider">Compliant</span>
            </div>
          </div>
        </div>

        {/* AI Assistant Legal Disclaimer */}
        <div className="mt-4 pt-3 border-t border-brand-sage/60 flex items-start gap-2 text-xs text-slate-600">
          <Info className="w-4 h-4 text-brand-navy flex-shrink-0 mt-0.5" />
          <p>
            <strong className="text-brand-navy">Statutory Notice:</strong> The AI engine performs evidentiary extraction under Rules 6 & 9 of the Legal Metrology (Packaged Commodities) Rules, 2011. Final statutory determination and notice issuance rests with the Legal Metrology Officer.
          </p>
        </div>
      </div>

      {/* Main Split Layout: Left Column (Dossier & Controls) + Right Column (Statutory Checklist) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* Left Column (5 cols): Package Photos, Retailer Meta, Actions */}
        <div className="lg:col-span-5 space-y-5">
          
          {/* Packaging Images Viewer */}
          <div className="bg-white rounded-md p-4 sm:p-5 border border-brand-sage shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-brand-navy uppercase tracking-wider">
                Captured Packaging Panels
              </h3>
              <span className="text-[10px] text-slate-500 font-mono">OCR Evidence Region</span>
            </div>

            {/* Main Active Image Display */}
            <div className="relative bg-slate-950 rounded-md overflow-hidden aspect-video border border-brand-sage flex items-center justify-center">
              <img
                src={product.packageImages[selectedImageTab]}
                alt="Package View"
                className="w-full h-full object-contain p-2"
              />
              <div className="absolute bottom-2 left-2 bg-[#061a2e]/90 text-brand-cream font-mono text-[10px] px-2 py-0.5 rounded border border-brand-sage/40">
                PANEL: {selectedImageTab.toUpperCase()}
              </div>
            </div>

            {/* Thumbnail Selectors */}
            <div className="grid grid-cols-4 gap-2 text-center text-[10px] font-semibold text-slate-600">
              <button
                onClick={() => setSelectedImageTab('back')}
                className={`p-1.5 rounded-md border transition-colors ${
                  selectedImageTab === 'back'
                    ? 'border-brand-navy bg-brand-navy text-white font-bold'
                    : 'border-brand-sage hover:bg-slate-50 text-brand-navy'
                }`}
              >
                Decl. Panel
              </button>
              <button
                onClick={() => setSelectedImageTab('front')}
                className={`p-1.5 rounded-md border transition-colors ${
                  selectedImageTab === 'front'
                    ? 'border-brand-navy bg-brand-navy text-white font-bold'
                    : 'border-brand-sage hover:bg-slate-50 text-brand-navy'
                }`}
              >
                Front View
              </button>
              <button
                onClick={() => setSelectedImageTab('mrpPanel')}
                className={`p-1.5 rounded-md border transition-colors ${
                  selectedImageTab === 'mrpPanel'
                    ? 'border-brand-navy bg-brand-navy text-white font-bold'
                    : 'border-brand-sage hover:bg-slate-50 text-brand-navy'
                }`}
              >
                Price Macro
              </button>
              <button
                onClick={() => setSelectedImageTab('barcode')}
                className={`p-1.5 rounded-md border transition-colors ${
                  selectedImageTab === 'barcode'
                    ? 'border-brand-navy bg-brand-navy text-white font-bold'
                    : 'border-brand-sage hover:bg-slate-50 text-brand-navy'
                }`}
              >
                Barcode/QR
              </button>
            </div>
          </div>

          {/* Surveillance & Retailer Dossier Card */}
          <div className="bg-white rounded-md p-5 border border-brand-sage shadow-sm space-y-3 text-xs">
            <h3 className="text-xs font-bold text-brand-navy uppercase tracking-wider border-b border-brand-sage/60 pb-2">
              Retailer & Package Audit File
            </h3>

            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">Retail Outlet:</span>
                <span className="font-bold text-brand-navy text-right">{product.storeDetails.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Proprietor:</span>
                <span className="font-semibold text-slate-700">{product.storeDetails.proprietor}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Retail Address:</span>
                <span className="text-slate-700 text-right max-w-[200px] truncate">{product.storeDetails.address}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Geo Stamp:</span>
                <span className="font-mono text-brand-navy font-semibold">{product.storeDetails.geoCoords}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Batch Stamp:</span>
                <span className="font-mono font-bold text-brand-navy">{product.batchNo}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Display Area:</span>
                <span className="font-mono text-slate-800">{product.principalDisplayArea} (Min H: {product.mandatoryNumeralHeightRequired})</span>
              </div>
            </div>
          </div>

          {/* Inspector Action & Notice Generator Block */}
          <div className="bg-white rounded-md p-5 border border-brand-sage shadow-sm space-y-4">
            <div className="flex items-center justify-between border-b border-brand-sage/60 pb-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-brand-navy">
                Official Regulatory Action
              </h3>
              <span className="text-[10px] bg-brand-cream/40 px-2 py-0.5 rounded font-mono text-brand-navy border border-brand-sage">
                LMO Circle 04
              </span>
            </div>

            {/* Notice under Section 32 button */}
            {violationCount > 0 ? (
              <button
                onClick={() => setShowNoticeModal(true)}
                className="w-full bg-red-700 hover:bg-red-800 text-white font-semibold rounded-md shadow-sm text-xs py-2.5 px-4 flex items-center justify-center gap-2 transition-colors"
              >
                <AlertOctagon className="w-4 h-4" />
                <span>Issue Rule 32 / Sec 39 Notice ({violationCount} Violations)</span>
              </button>
            ) : (
              <div className="p-2.5 bg-emerald-50 rounded-md border border-emerald-300 text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-700 flex-shrink-0" />
                <span>Zero statutory contraventions detected. Cleared for retail distribution.</span>
              </div>
            )}

            {/* Officer Inspection Signature */}
            <div className="pt-2 border-t border-brand-sage/60 space-y-2">
              <label className="block text-xs text-brand-navy font-semibold">
                Officer Field Remarks (Optional):
              </label>
              <textarea
                value={inspectorNotes}
                onChange={(e) => setInspectorNotes(e.target.value)}
                placeholder="Enter field observations, trader statements, or compounding remarks..."
                className="w-full p-2 text-xs rounded-md bg-slate-50 border border-brand-sage text-brand-navy placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-navy h-20 resize-none"
              />

              {/* Primary Confirm Button: bg-brand-navy hover:bg-[#061a2e] */}
              <button
                onClick={() => setIsReportConfirmed(true)}
                disabled={isReportConfirmed}
                className={`w-full py-2.5 px-4 rounded-md font-semibold text-xs flex items-center justify-center gap-2 transition-colors shadow-sm ${
                  isReportConfirmed
                    ? 'bg-emerald-700 text-white cursor-default'
                    : 'bg-brand-navy hover:bg-[#061a2e] text-white'
                }`}
              >
                {isReportConfirmed ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Inspection Record Signed & Stamped</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck className="w-4 h-4" />
                    <span>Confirm & Sign Field Inspection</span>
                  </>
                )}
              </button>
            </div>
          </div>

        </div>

        {/* Right Column (7 cols): Checklist of Statutory Declarations */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-brand-sage/60">
            <div>
              <h2 className="text-base font-bold text-brand-navy tracking-tight">
                Mandatory Declarations Checklist
              </h2>
              <p className="text-xs text-slate-500">
                Statutory audit under Rules 6 & 9 of Legal Metrology (Packaged Commodities) Rules, 2011
              </p>
            </div>
            <span className="text-xs font-mono font-bold text-brand-navy bg-brand-cream/40 px-2.5 py-1 rounded-md border border-brand-sage">
              7 Statutory Checks
            </span>
          </div>

          {/* Checklist Cards: Pure bg-white with border-brand-sage and sharp left border */}
          <div className="space-y-3">
            {currentDeclarations.map((item) => {
              const isItemViolation = item.currentStatus === 'violation';
              const isItemReview = item.currentStatus === 'review';
              const isOverridden = overrides[item.id] !== undefined;

              const cardAccent = isItemViolation
                ? 'border-l-4 border-l-red-600'
                : isItemReview
                ? 'border-l-4 border-l-amber-500'
                : 'border-l-4 border-l-emerald-600';

              return (
                <div
                  key={item.id}
                  className={`bg-white rounded-md border border-brand-sage ${cardAccent} p-4 sm:p-5 shadow-sm transition-all`}
                >
                  {/* Card Top Row */}
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2.5 border-b border-brand-sage/40">
                    <div>
                      <span className="text-[11px] font-mono font-bold text-brand-navy bg-brand-cream/30 border border-brand-sage px-2 py-0.5 rounded mr-2">
                        {item.ruleCitation}
                      </span>
                      <h3 className="text-sm font-bold text-brand-navy mt-1 inline-block sm:block">
                        {item.title}
                      </h3>
                    </div>
                    <div className="flex items-center gap-2">
                      {isOverridden && (
                        <span className="text-[10px] font-bold bg-brand-cream/40 text-brand-navy px-2 py-0.5 rounded font-mono border border-brand-sage">
                          OVERRIDDEN
                        </span>
                      )}
                      <StatusBadge status={item.currentStatus} size="sm" />
                    </div>
                  </div>

                  {/* Card Body: Extracted text vs Requirement */}
                  <div className="mt-3 space-y-2 text-xs">
                    <div className="bg-slate-50 p-2.5 rounded-md border border-brand-sage/60 font-mono space-y-1">
                      <div className="flex justify-between text-[11px] text-slate-500 font-sans">
                        <span>Verbatim OCR Extraction:</span>
                        <span className="font-mono text-brand-navy font-bold">Conf: {item.aiConfidence}%</span>
                      </div>
                      <div className="text-brand-navy font-bold">
                        "{item.extractedText}"
                      </div>
                    </div>

                    {/* AI Reasoning / Defect Notice */}
                    {(isItemViolation || isItemReview) && (
                      <div className={`p-2.5 rounded-md text-xs leading-relaxed ${
                        isItemViolation ? 'bg-red-50 text-red-900 border border-red-200' : 'bg-amber-50 text-amber-900 border border-amber-200'
                      }`}>
                        <strong>AI Finding:</strong> {item.aiReasoning}
                      </div>
                    )}

                    <p className="text-[11px] text-slate-600 leading-normal">
                      <strong className="text-brand-navy">Legal Requirement:</strong> {item.statutoryRequirement}
                    </p>
                  </div>

                  {/* Card Bottom: Evidence Button & Inspector Override */}
                  <div className="mt-4 pt-3 border-t border-brand-sage/40 flex flex-wrap items-center justify-between gap-3">
                    
                    {/* View Evidence Button */}
                    <button
                      onClick={() => setActiveEvidenceDeclaration(item)}
                      className={`px-3.5 py-1.5 text-xs font-semibold rounded-md flex items-center gap-1.5 shadow-sm transition-colors ${
                        isItemViolation
                          ? 'bg-red-700 hover:bg-red-800 text-white'
                          : isItemReview
                          ? 'bg-amber-700 hover:bg-amber-800 text-white'
                          : 'bg-slate-50 hover:bg-brand-cream/40 text-brand-navy border border-brand-sage'
                      }`}
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>View Evidence & Caliper Analysis</span>
                    </button>

                    {/* Inspector Override Dropdown */}
                    <div className="flex items-center gap-1.5 text-xs">
                      <span className="text-slate-600 text-[11px] font-medium hidden sm:inline">
                        Inspector Decision:
                      </span>
                      <select
                        value={item.currentStatus}
                        onChange={(e) => handleOverride(item.id, e.target.value)}
                        className="text-xs font-semibold bg-white border border-brand-sage rounded-md px-2 py-1 text-brand-navy focus:outline-none focus:ring-1 focus:ring-brand-navy"
                      >
                        <option value="compliant">Confirm Compliant</option>
                        <option value="violation">Flag as Violation</option>
                        <option value="review">Flag for Lab Review</option>
                        <option value="waived">Waive / Warning</option>
                      </select>
                    </div>

                  </div>

                </div>
              );
            })}
          </div>

        </div>

      </div>

      {/* Interactive Evidence Modal */}
      {activeEvidenceDeclaration && (
        <EvidenceModal
          declaration={activeEvidenceDeclaration}
          onClose={() => setActiveEvidenceDeclaration(null)}
          onOverrideStatus={handleOverride}
        />
      )}

      {/* Official Form 32 / 39 Notice Modal */}
      {showNoticeModal && (
        <NoticeModal
          inspection={product}
          violations={activeViolations}
          onClose={() => setShowNoticeModal(false)}
        />
      )}

    </div>
  );
}
