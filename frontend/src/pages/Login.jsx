import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, User, MapPin, KeyRound, ArrowRight, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { OFFICER_PROFILE } from '../mockData';
import { loginOfficer } from '../api';

export default function Login() {
  const navigate = useNavigate();
  const [officerId, setOfficerId] = useState(OFFICER_PROFILE.badgeId);
  const [pin, setPin] = useState('8842');
  const [circle, setCircle] = useState('North Delhi - Circle 04');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');
    const res = await loginOfficer(officerId, pin, circle);
    setLoading(false);
    if (res.success) {
      navigate('/inspector-home');
    } else {
      setErrorMsg(res.error || 'Authentication failed. Check your ID and PIN.');
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col justify-center items-center px-4 py-8">
      <div className="w-full max-w-md">
        
        {/* Emblem & Portal Title */}
        <div className="text-center mb-6 space-y-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-md bg-brand-navy text-brand-cream shadow-sm border border-brand-sage/40 p-2.5 mb-1">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-brand-navy">
            NiyamDrishti <span className="text-brand-bronze">AI</span>
          </h1>
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-600">
            Department of Consumer Affairs &bull; Legal Metrology Division
          </p>
          <div className="inline-block px-3 py-1 bg-brand-cream/40 border border-brand-sage rounded text-[11px] font-bold text-brand-navy font-mono">
            Government Compliance Inspection Terminal
          </div>
        </div>

        {/* Login Card: Pure bg-white with border-brand-sage */}
        <div className="bg-white rounded-md shadow-sm border border-brand-sage overflow-hidden">
          <div className="bg-brand-navy px-6 py-3.5 border-b border-[#061a2e] text-white flex justify-between items-center">
            <div>
              <h2 className="text-xs font-bold tracking-wider uppercase text-brand-cream">Officer Authentication</h2>
              <p className="text-[11px] text-slate-300">Enforcement Portal Access</p>
            </div>
            <span className="text-[10px] bg-[#061a2e] text-emerald-400 px-2 py-0.5 rounded border border-white/10 font-mono">
              SECURE
            </span>
          </div>

          <form onSubmit={handleLogin} className="p-6 space-y-4">
            {/* Officer ID */}
            <div>
              <label className="block text-xs font-bold text-brand-navy uppercase tracking-wider mb-1">
                Legal Metrology Officer ID
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-brand-bronze absolute left-3 top-3" />
                <input
                  type="text"
                  value={officerId}
                  onChange={(e) => setOfficerId(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2 text-xs font-mono font-medium rounded-md border border-brand-sage focus:outline-none focus:ring-1 focus:ring-brand-navy focus:border-brand-navy bg-slate-50/50 text-brand-navy"
                  placeholder="e.g. LMO-DEL-2024-884"
                />
              </div>
            </div>

            {/* Jurisdiction / Circle */}
            <div>
              <label className="block text-xs font-bold text-brand-navy uppercase tracking-wider mb-1">
                Enforcement Circle / Zone
              </label>
              <div className="relative">
                <MapPin className="w-4 h-4 text-brand-bronze absolute left-3 top-3" />
                <select
                  value={circle}
                  onChange={(e) => setCircle(e.target.value)}
                  className="w-full pl-9 pr-3 py-2 text-xs font-medium rounded-md border border-brand-sage focus:outline-none focus:ring-1 focus:ring-brand-navy focus:border-brand-navy bg-slate-50/50 text-brand-navy"
                >
                  <option value="North Delhi - Circle 04">North Delhi - Circle 04 (Kamla Nagar, Model Town)</option>
                  <option value="Central Delhi - Circle 01">Central Delhi - Circle 01 (Connaught Place, Karol Bagh)</option>
                  <option value="South Delhi - Circle 07">South Delhi - Circle 07 (Saket, Hauz Khas)</option>
                  <option value="West Delhi - Circle 03">West Delhi - Circle 03 (Rajouri Garden, Punjabi Bagh)</option>
                </select>
              </div>
            </div>

            {/* Officer PIN */}
            <div>
              <label className="block text-xs font-bold text-brand-navy uppercase tracking-wider mb-1">
                Security PIN / Token
              </label>
              <div className="relative">
                <KeyRound className="w-4 h-4 text-brand-bronze absolute left-3 top-3" />
                <input
                  type="password"
                  value={pin}
                  onChange={(e) => setPin(e.target.value)}
                  required
                  className="w-full pl-9 pr-3 py-2 text-xs font-mono font-medium rounded-md border border-brand-sage focus:outline-none focus:ring-1 focus:ring-brand-navy focus:border-brand-navy bg-slate-50/50 text-brand-navy"
                  placeholder="Enter 4-digit PIN"
                />
              </div>
            </div>

            {/* Credential Hint */}
            <div className="p-3 bg-brand-cream/30 rounded-md border border-brand-sage text-[11px] text-brand-navy space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-brand-navy">
                <CheckCircle2 className="w-3.5 h-3.5 text-brand-navy" />
                <span>Authorised Field Officer Profile Pre-Loaded</span>
              </div>
              <p className="text-slate-600">
                Credentials for Officer <strong>Rajesh Sharma (LMO-DEL-2024-884)</strong> loaded for inspection simulation.
              </p>
            </div>

            {/* Submit Button: bg-brand-navy hover:bg-[#061a2e] */}
            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 bg-brand-navy hover:bg-[#061a2e] text-white font-semibold text-xs py-2.5 px-4 rounded-md shadow-sm flex items-center justify-center gap-2 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-navy"
            >
              <span>{loading ? 'Authenticating Officer Token...' : 'Access Inspection Terminal'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Legal Warning Notice */}
          <div className="bg-slate-50 p-4 border-t border-brand-sage/60 text-[11px] text-slate-600 flex items-start gap-2">
            <ShieldAlert className="w-4 h-4 text-brand-bronze flex-shrink-0 mt-0.5" />
            <p>
              <strong>Official Notice:</strong> Access restricted to authorized Enforcement Officers under the Legal Metrology Act, 2009. Inspections are auditable and geo-tagged.
            </p>
          </div>
        </div>

        <p className="text-center text-xs text-slate-500 mt-6 font-mono">
          NiyamDrishti AI &bull; Version 1.0.0 (SIH)
        </p>

      </div>
    </div>
  );
}
