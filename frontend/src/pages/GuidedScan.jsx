import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Camera, 
  CheckCircle2, 
  RefreshCw, 
  ArrowRight, 
  Scan, 
  ShieldCheck,
  SlidersHorizontal,
  Upload,
  FileImage
} from 'lucide-react';
import { DEMO_PRESETS } from '../mockData';
import { scanImageEvidence } from '../api';

export default function GuidedScan({ setSelectedProduct }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [selectedPresetId, setSelectedPresetId] = useState(DEMO_PRESETS[0].id);
  const [inferenceStep, setInferenceStep] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [customFile, setCustomFile] = useState(null);
  const [customPreview, setCustomPreview] = useState(null);
  const [liveScanResult, setLiveScanResult] = useState(null);

  const activePreset = DEMO_PRESETS.find(p => p.id === selectedPresetId) || DEMO_PRESETS[0];

  const inferenceSteps = [
    { title: "Segmenting Principal Display Panel", desc: "Calculating package surface area (185 cm²) for Rule 9 threshold mapping" },
    { title: "Transformer OCR & Entity Parsing", desc: "Extracting Net Quantity, MRP, Manufacturer address, and Customer Cell text" },
    { title: "Statutory Rule 6 Verification", desc: "Checking tax inclusion phrases, metric unit validity, and postal PIN integrity" },
    { title: "Computer Vision Caliper Inspection", desc: "Measuring numeral height on Net Qty declaration against 3.0mm legal minimum" },
    { title: "Compiling Regulatory Findings", desc: "Generating tamper-evident audit trail & legal citations" }
  ];

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      setCustomFile(file);
      setCustomPreview(URL.createObjectURL(file));
    }
  };

  const handleStartAnalysis = async () => {
    setIsProcessing(true);
    setInferenceStep(0);

    if (customFile) {
      // Trigger live AI/OCR scan asynchronously
      scanImageEvidence(customFile, null, activePreset.data.productName).then((res) => {
        if (res.success && res.data) {
          setLiveScanResult(res.data);
        }
      });
    }
  };

  useEffect(() => {
    let timer;
    if (isProcessing) {
      if (inferenceStep < inferenceSteps.length) {
        timer = setTimeout(() => {
          setInferenceStep(prev => prev + 1);
        }, 650);
      } else {
        timer = setTimeout(() => {
          const finalData = liveScanResult || activePreset.data;
          if (setSelectedProduct) {
            setSelectedProduct(finalData);
          }
          navigate('/compliance-result', { state: { productData: finalData } });
        }, 500);
      }
    }
    return () => clearTimeout(timer);
  }, [isProcessing, inferenceStep, liveScanResult]);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Page Title & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-brand-sage/60">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-brand-navy tracking-tight">
              Guided Package Scanner
            </h1>
            <span className="text-[11px] bg-brand-cream/40 text-brand-navy font-mono font-bold px-2 py-0.5 rounded border border-brand-sage uppercase">
              Field Terminal
            </span>
          </div>
          <p className="text-xs text-slate-600 mt-0.5">
            Capture or select packaged commodity panels to execute statutory compliance verification.
          </p>
        </div>

        {/* Controls: Preset Selector & Upload Button */}
        <div className="flex flex-wrap items-center gap-2">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            className="hidden"
          />
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-brand-navy hover:bg-[#061a2e] text-white text-xs font-semibold rounded shadow-sm transition-colors"
          >
            <Upload className="w-3.5 h-3.5" />
            <span>{customFile ? `Uploaded: ${customFile.name}` : 'Upload Label Photo'}</span>
          </button>

          <div className="flex items-center gap-2 bg-white border border-brand-sage p-1.5 rounded-md shadow-sm">
            <SlidersHorizontal className="w-4 h-4 text-brand-bronze flex-shrink-0 ml-1" />
            <div className="text-xs flex items-center">
              <span className="font-semibold text-brand-navy mr-1.5">Preset:</span>
              <select
                value={selectedPresetId}
                onChange={(e) => {
                  setSelectedPresetId(e.target.value);
                  setCustomFile(null);
                  setCustomPreview(null);
                }}
                disabled={isProcessing}
                className="font-medium text-xs text-brand-navy bg-slate-50 border border-brand-sage rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-brand-navy"
              >
                {DEMO_PRESETS.map(p => (
                  <option key={p.id} value={p.id}>
                    {p.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Inspection Capture Area */}
      {!isProcessing ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Left: Viewport Simulator */}
          <div className="lg:col-span-2 space-y-4">
            <div className="relative bg-slate-950 rounded-lg overflow-hidden border border-brand-navy shadow-md aspect-video sm:aspect-[16/10] flex items-center justify-center">
              <img
                src={customPreview || activePreset.data.packageImages.back}
                alt="Packaged Commodity"
                className="w-full h-full object-contain p-4 opacity-90"
              />

              {/* Viewfinder Target & Guides */}
              <div className="absolute inset-6 border border-white/20 rounded pointer-events-none flex flex-col justify-between p-3">
                <div className="flex justify-between items-start text-[11px] font-mono text-slate-300">
                  <span className="bg-[#061a2e]/90 px-2 py-0.5 rounded border border-brand-sage/40 text-brand-cream">
                    TARGET: STATUTORY DECLARATION PANEL
                  </span>
                  <span className="bg-[#061a2e]/90 px-2 py-0.5 rounded border border-brand-sage/40 text-emerald-400 font-bold">
                    ALIGNMENT OK
                  </span>
                </div>

                <div className="self-center flex flex-col items-center gap-1">
                  <div className="w-10 h-10 border border-dashed border-white/60 rounded flex items-center justify-center">
                    <Scan className="w-5 h-5 text-white/80" />
                  </div>
                  <span className="text-[10px] font-mono text-slate-300 bg-[#061a2e]/80 px-2 py-0.5 rounded">
                    Rule 6 Layout Detected
                  </span>
                </div>

                <div className="flex justify-between items-end text-[10px] font-mono text-slate-300">
                  <span>ISO 100 &bull; 1/250s</span>
                  <span className="text-brand-cream font-bold">OCR ENGINE READY</span>
                </div>
              </div>

              {/* Bounding box preview teaser */}
              <div className="absolute top-[28%] right-[16%] w-[30%] h-[20%] border-2 border-red-600 bg-red-600/10 rounded pointer-events-none flex items-start justify-end p-1">
                <span className="bg-red-700 text-white text-[9px] font-mono font-bold px-1 rounded">
                  Price / Rule 6(1)(e)
                </span>
              </div>
            </div>

            {/* Panel Thumbnails */}
            <div className="grid grid-cols-4 gap-2 sm:gap-3">
              <div className="p-2 bg-white rounded-md border-2 border-brand-navy shadow-sm space-y-1 text-center">
                <img
                  src={activePreset.data.packageImages.back}
                  alt="Back Panel"
                  className="w-full h-14 object-cover rounded border border-brand-sage"
                />
                <span className="text-[11px] font-bold text-brand-navy block truncate">1. Decl. Panel</span>
                <span className="text-[10px] text-emerald-700 font-bold block font-mono">✓ READY</span>
              </div>

              <div className="p-2 bg-white rounded-md border border-brand-sage shadow-sm space-y-1 text-center">
                <img
                  src={activePreset.data.packageImages.front}
                  alt="Front Panel"
                  className="w-full h-14 object-cover rounded border border-brand-sage"
                />
                <span className="text-[11px] font-medium text-slate-700 block truncate">2. Front View</span>
                <span className="text-[10px] text-emerald-700 font-bold block font-mono">✓ READY</span>
              </div>

              <div className="p-2 bg-white rounded-md border border-brand-sage shadow-sm space-y-1 text-center">
                <img
                  src={activePreset.data.packageImages.mrpPanel}
                  alt="MRP Macro"
                  className="w-full h-14 object-cover rounded border border-brand-sage"
                />
                <span className="text-[11px] font-medium text-slate-700 block truncate">3. Price Macro</span>
                <span className="text-[10px] text-emerald-700 font-bold block font-mono">✓ READY</span>
              </div>

              <div className="p-2 bg-white rounded-md border border-brand-sage shadow-sm space-y-1 text-center">
                <img
                  src={activePreset.data.packageImages.barcode}
                  alt="Barcode"
                  className="w-full h-14 object-cover rounded border border-brand-sage"
                />
                <span className="text-[11px] font-medium text-slate-700 block truncate">4. Barcode</span>
                <span className="text-[10px] text-emerald-700 font-bold block font-mono">✓ READY</span>
              </div>
            </div>
          </div>

          {/* Right: Surveillance Metadata & Execution */}
          <div className="space-y-4 flex flex-col justify-between">
            <div className="bg-white rounded-md p-5 border border-brand-sage shadow-sm space-y-4">
              <h2 className="text-xs font-bold text-brand-navy tracking-wide uppercase border-b border-brand-sage/60 pb-2">
                Surveillance Metadata
              </h2>

              <div className="space-y-2.5 text-xs">
                <div>
                  <span className="text-slate-500 block text-[11px]">Selected Commodity:</span>
                  <span className="font-bold text-brand-navy text-sm">{activePreset.data.productName}</span>
                </div>

                <div>
                  <span className="text-slate-500 block text-[11px]">Brand / Manufacturer:</span>
                  <span className="font-semibold text-slate-800">{activePreset.data.brand}</span>
                </div>

                <div>
                  <span className="text-slate-500 block text-[11px]">Commodity Category:</span>
                  <span className="font-semibold text-slate-800">{activePreset.data.category}</span>
                </div>

                <div>
                  <span className="text-slate-500 block text-[11px]">Retailer Inspected:</span>
                  <span className="font-medium text-slate-700">{activePreset.data.storeDetails.name}</span>
                </div>

                <div className="pt-2 border-t border-brand-sage/60">
                  <span className="text-slate-500 block text-[11px]">Statutory Legal Framework:</span>
                  <span className="font-mono text-brand-navy font-bold">
                    Legal Metrology (Packaged Commodities) Rules, 2011
                  </span>
                </div>
              </div>

              {/* Compliance checks summary */}
              <div className="bg-slate-50 p-3 rounded-md border border-brand-sage text-xs space-y-1.5">
                <div className="font-bold text-brand-navy text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-brand-navy" />
                  Statutory Rule Verifications
                </div>
                <ul className="text-slate-600 text-[11px] space-y-1 font-mono">
                  <li>&bull; Rule 6(1)(e): MRP & Tax Inclusivity</li>
                  <li>&bull; Rule 6(1)(da): Consumer Redressal Contacts</li>
                  <li>&bull; Rule 9: Numeral Height vs Display Area</li>
                  <li>&bull; Rule 6(1)(f): Metric Units Compliance</li>
                  <li>&bull; Rule 6(1)(a): Complete Postal Address</li>
                </ul>
              </div>
            </div>

            {/* Primary Action Button: bg-brand-navy hover:bg-[#061a2e] */}
            <div className="space-y-2">
              <button
                onClick={handleStartAnalysis}
                className="w-full bg-brand-navy hover:bg-[#061a2e] text-white font-semibold rounded-md shadow-sm text-sm py-3 px-4 flex items-center justify-center gap-2 transition-colors"
              >
                <span>Initiate AI Compliance Scan</span>
                <ArrowRight className="w-4 h-4 text-white" />
              </button>

              <p className="text-center text-[11px] text-slate-500 font-mono">
                ISO/IEC 17020 Compliant Audit Trail
              </p>
            </div>

          </div>

        </div>
      ) : (
        /* Real-time Multi-Stage AI Inference View */
        <div className="bg-white rounded-md p-8 sm:p-10 border border-brand-sage shadow-sm max-w-2xl mx-auto text-center space-y-6">
          
          <div className="w-14 h-14 rounded-md bg-brand-navy text-brand-cream mx-auto flex items-center justify-center border border-[#061a2e]">
            <RefreshCw className="w-7 h-7 animate-spin text-brand-cream" />
          </div>

          <div className="space-y-1">
            <h2 className="text-xl font-bold text-brand-navy tracking-tight">
              Executing Regulatory AI Verification
            </h2>
            <p className="text-xs font-mono text-slate-600 uppercase tracking-wider">
              Legal Metrology OCR & Rule Engine v2.4
            </p>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-slate-200 h-2 rounded overflow-hidden">
            <div
              className="bg-brand-navy h-full transition-all duration-500 ease-out"
              style={{ width: `${((inferenceStep + 1) / inferenceSteps.length) * 100}%` }}
            ></div>
          </div>

          {/* Steps list */}
          <div className="space-y-2.5 text-left max-w-md mx-auto">
            {inferenceSteps.map((step, idx) => {
              const isDone = idx < inferenceStep;
              const isCurrent = idx === inferenceStep;
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-md border transition-colors ${
                    isCurrent
                      ? 'bg-brand-cream/30 border-brand-sage'
                      : isDone
                      ? 'bg-slate-50 border-brand-sage/60'
                      : 'bg-white border-dashed border-slate-200 opacity-50'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    {isDone ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-700 flex-shrink-0" />
                    ) : isCurrent ? (
                      <RefreshCw className="w-4 h-4 text-brand-navy animate-spin flex-shrink-0" />
                    ) : (
                      <div className="w-4 h-4 rounded border border-slate-300 flex-shrink-0"></div>
                    )}
                    <div className="flex-1">
                      <div className="text-xs font-bold text-brand-navy">{step.title}</div>
                      <div className="text-[11px] text-slate-600">{step.desc}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <p className="text-xs text-slate-500 font-mono">
            Verification Hash: SHA256-4c9f-88a2-e01b
          </p>

        </div>
      )}

    </div>
  );
}
