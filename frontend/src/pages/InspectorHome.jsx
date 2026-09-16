import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Camera, 
  Search, 
  ChevronRight, 
  MapPin, 
  Clock, 
  Store, 
  FileCheck2,
  AlertOctagon,
  AlertTriangle,
  CheckCircle2,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import { OFFICER_PROFILE, RECENT_SCANS } from '../mockData';
import { fetchDashboardStats, getStoredOfficer } from '../api';

export default function InspectorHome() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [officer, setOfficer] = useState(OFFICER_PROFILE);
  const [scans, setScans] = useState(RECENT_SCANS);
  const [stats, setStats] = useState({
    total_inspections: OFFICER_PROFILE.activeInspectionsToday,
    compliant: 10,
    violations: OFFICER_PROFILE.violationsDetectedToday,
    review_required: 1,
    pending: 0,
  });
  const [isLive, setIsLive] = useState(false);

  useEffect(() => {
    setOfficer(getStoredOfficer());
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    const res = await fetchDashboardStats();
    if (res.stats) {
      setStats(res.stats);
      if (res.recentScans && res.recentScans.length > 0) {
        setScans(res.recentScans);
      }
      setIsLive(res.live);
    }
  };

  const filteredScans = scans.filter((scan) => {
    const matchesFilter = filter === 'all' || scan.overallStatus === filter;
    const matchesSearch = 
      scan.productName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scan.storeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      scan.category.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Officer Authority Header Card: Pure bg-white with border-brand-sage */}
      <div className="bg-white rounded-md p-5 sm:p-6 border border-brand-sage shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          {/* Officer Avatar with brand-bronze */}
          <div className="w-12 h-12 rounded-md bg-brand-bronze text-white flex items-center justify-center font-bold text-base shadow-sm flex-shrink-0">
            RS
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-brand-navy tracking-tight">
                Inspector {OFFICER_PROFILE.name}
              </h1>
              <span className="text-[11px] bg-brand-cream/40 text-brand-navy border border-brand-sage font-bold px-2 py-0.5 rounded uppercase font-mono">
                Active Field Duty
              </span>
            </div>
            <p className="text-xs text-slate-600 font-medium mt-0.5">
              {OFFICER_PROFILE.designation} &bull; <span className="font-mono font-bold text-brand-navy">{OFFICER_PROFILE.badgeId}</span>
            </p>
            <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
              <MapPin className="w-3.5 h-3.5 text-brand-bronze" />
              <span>{OFFICER_PROFILE.zone}</span>
            </p>
          </div>
        </div>

        {/* Primary Action Button: bg-brand-navy hover:bg-[#061a2e] */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/guided-scan')}
            className="w-full sm:w-auto bg-brand-navy hover:bg-[#061a2e] text-white font-semibold rounded-md shadow-sm text-sm px-5 py-2.5 flex items-center justify-center gap-2 transition-colors"
          >
            <Camera className="w-4 h-4 text-white" />
            <span>Start New Inspection</span>
          </button>
        </div>
      </div>

      {/* Strict Semantic Metric Cards with border-brand-sage */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Scans Total"
          value={stats.total_inspections}
          subtitle="Enforcement database"
          icon={FileCheck2}
          color="blue"
          trend={isLive ? "Live API connected" : "Offline mode"}
        />
        <MetricCard
          title="Violations Flagged"
          value={stats.violations}
          subtitle="Rule 6 & 9 contraventions"
          icon={AlertOctagon}
          color="red"
          trend="Statutory notice required"
        />
        <MetricCard
          title="Review Required"
          value={stats.review_required}
          subtitle="Human review needed"
          icon={AlertTriangle}
          color="amber"
          trend="Action pending"
        />
        <MetricCard
          title="Compliant Units"
          value={stats.compliant}
          subtitle="Fully compliant labels"
          icon={CheckCircle2}
          color="emerald"
          trend="Rule-verified"
        />
      </div>

      {/* Enforcement Command Banner: bg-brand-navy */}
      <div className="bg-brand-navy rounded-md p-5 text-white border border-brand-navy shadow-sm flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="space-y-1 text-center sm:text-left">
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <span className="p-1 bg-[#061a2e] text-brand-cream rounded border border-brand-sage/20">
              <ShieldCheck className="w-4 h-4 text-brand-cream" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-brand-cream font-mono">
              Legal Metrology Surveillance Terminal
            </span>
          </div>
          <h2 className="text-base font-bold text-white">
            Conduct Package Verification under PCR, 2011
          </h2>
          <p className="text-xs text-slate-300 max-w-xl">
            Automated verification of Net Quantity, MRP, Manufacturer address, Consumer Helpline, and Rule 9 font height standards.
          </p>
        </div>

        {/* Primary Action Button */}
        <button
          onClick={() => navigate('/guided-scan')}
          className="bg-white hover:bg-brand-cream text-brand-navy font-semibold rounded-md shadow-sm text-xs px-4 py-2.5 flex items-center gap-2 transition-colors flex-shrink-0"
        >
          <Camera className="w-4 h-4 text-brand-navy" />
          <span>Launch AI Scanner</span>
        </button>
      </div>

      {/* Recent Inspections Surveillance Log: bg-white with border-brand-sage */}
      <div className="bg-white rounded-md p-5 sm:p-6 border border-brand-sage shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-brand-sage/60">
          <div>
            <h2 className="text-base font-bold text-brand-navy tracking-tight">
              Recent Market Surveillance Scans
            </h2>
            <p className="text-xs text-slate-500">
              Official audit log of packaged commodities examined during current duty tour
            </p>
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search product or retailer..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-md border border-brand-sage focus:outline-none focus:ring-1 focus:ring-brand-navy focus:border-brand-navy bg-slate-50/50 text-brand-navy"
            />
          </div>
        </div>

        {/* Filter Buttons */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <button
            onClick={() => setFilter('all')}
            className={`px-3 py-1 rounded-md font-semibold transition-colors ${
              filter === 'all'
                ? 'bg-brand-navy text-white'
                : 'bg-slate-100 text-brand-navy hover:bg-brand-cream/40 border border-brand-sage'
            }`}
          >
            All Logs ({RECENT_SCANS.length})
          </button>
          <button
            onClick={() => setFilter('violation')}
            className={`px-3 py-1 rounded-md font-semibold flex items-center gap-1.5 transition-colors ${
              filter === 'violation'
                ? 'bg-red-700 text-white'
                : 'bg-red-50 text-red-800 hover:bg-red-100 border border-red-200'
            }`}
          >
            <AlertOctagon className="w-3.5 h-3.5" />
            <span>Violations (2)</span>
          </button>
          <button
            onClick={() => setFilter('review')}
            className={`px-3 py-1 rounded-md font-semibold flex items-center gap-1.5 transition-colors ${
              filter === 'review'
                ? 'bg-amber-700 text-white'
                : 'bg-amber-50 text-amber-800 hover:bg-amber-100 border border-amber-300'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Review Required (1)</span>
          </button>
          <button
            onClick={() => setFilter('compliant')}
            className={`px-3 py-1 rounded-md font-semibold flex items-center gap-1.5 transition-colors ${
              filter === 'compliant'
                ? 'bg-emerald-700 text-white'
                : 'bg-emerald-50 text-emerald-800 hover:bg-emerald-100 border border-emerald-300'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Compliant (1)</span>
          </button>
        </div>

        {/* Surveillance List Feed */}
        <div className="space-y-3">
          {filteredScans.length === 0 ? (
            <div className="text-center py-10 text-slate-500 text-xs">
              No inspection records found matching criteria.
            </div>
          ) : (
            filteredScans.map((scan) => (
              <div
                key={scan.id}
                onClick={() => navigate('/compliance-result')}
                className="group p-4 rounded-md border border-brand-sage hover:border-brand-navy bg-white hover:bg-brand-cream/15 shadow-sm transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-start gap-3">
                  <img
                    src={scan.thumbnail}
                    alt={scan.productName}
                    className="w-14 h-14 rounded-md object-cover border border-brand-sage flex-shrink-0"
                  />
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-bold text-brand-navy group-hover:underline transition-colors">
                        {scan.productName}
                      </span>
                      <span className="text-xs text-slate-500 font-medium">
                        ({scan.variant})
                      </span>
                      <StatusBadge status={scan.overallStatus} size="sm" />
                    </div>

                    <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
                      <span className="flex items-center gap-1">
                        <Store className="w-3.5 h-3.5 text-brand-bronze" />
                        <strong className="text-brand-navy">{scan.storeName}</strong>
                      </span>
                      <span>&bull;</span>
                      <span className="flex items-center gap-1 font-mono text-[11px] text-slate-500">
                        <Clock className="w-3 h-3 text-slate-400" />
                        {scan.inspectedAt}
                      </span>
                    </div>

                    <div className="text-[11px] text-slate-500 flex items-center gap-3">
                      <span>GTIN: <code className="font-mono text-brand-navy font-semibold">{scan.gtin}</code></span>
                      <span>&bull;</span>
                      <span className="text-slate-600 font-medium">
                        {scan.violationCount > 0 && <span className="text-red-700 font-bold">{scan.violationCount} Violations &bull; </span>}
                        {scan.reviewCount > 0 && <span className="text-amber-700 font-bold">{scan.reviewCount} Review Req. &bull; </span>}
                        <span className="text-emerald-700">{scan.compliantCount} Compliant</span>
                      </span>
                    </div>
                  </div>
                </div>

                {/* Right side status & action */}
                <div className="flex items-center justify-between sm:justify-end gap-3 pt-2 sm:pt-0 border-t sm:border-t-0 border-brand-sage/40">
                  <div className="text-right hidden md:block">
                    <div className="text-xs font-mono font-bold text-brand-navy">
                      Conf: {scan.overallConfidence}%
                    </div>
                    <div className="text-[10px] font-mono text-slate-400">
                      {scan.id}
                    </div>
                  </div>

                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      navigate('/compliance-result');
                    }}
                    className="px-3.5 py-1.5 text-xs font-semibold bg-slate-50 hover:bg-brand-navy hover:text-white text-brand-navy border border-brand-sage rounded-md flex items-center gap-1.5 transition-colors shadow-sm"
                  >
                    <span>Inspect Record</span>
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

    </div>
  );
}
