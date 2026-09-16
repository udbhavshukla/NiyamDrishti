import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, 
  Camera, 
  FileText, 
  Home, 
  LogOut, 
  MapPin, 
  Radio, 
  Menu, 
  X, 
  UserCheck, 
  ChevronRight
} from 'lucide-react';
import { OFFICER_PROFILE } from '../mockData';

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isLoginPage = location.pathname === '/login';

  const navLinks = [
    { name: 'Inspector Home', path: '/inspector-home', icon: Home },
    { name: 'Start Inspection', path: '/guided-scan', icon: Camera },
    { name: 'Latest Scan Result', path: '/compliance-result', icon: FileText },
  ];

  return (
    <header className="sticky top-0 z-40 bg-brand-navy border-b border-[#061a2e] text-white shadow-md">
      {/* Top Government Authority Strip */}
      <div className="bg-[#061a2e] px-4 py-1.5 text-xs text-slate-300 border-b border-white/10 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="inline-block w-2 h-2 rounded-full bg-orange-500"></span>
          <span className="inline-block w-2 h-2 rounded-full bg-white"></span>
          <span className="inline-block w-2 h-2 rounded-full bg-green-600"></span>
          <span className="font-semibold tracking-wider text-brand-cream text-[11px] uppercase">
            Government of India &bull; Ministry of Consumer Affairs &bull; Legal Metrology Enforcement
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-4 text-[11px]">
          {/* Subtle brand-bronze / cream offline mode badge */}
          <span className="flex items-center gap-1.5 text-brand-cream font-medium font-mono">
            <Radio className="w-3 h-3 text-emerald-400" />
            Field Terminal Online (Circle 04)
          </span>
          <span className="text-slate-500">|</span>
          <span className="flex items-center gap-1 text-slate-300 font-mono">
            <MapPin className="w-3 h-3 text-brand-cream" />
            Kamla Nagar, North Delhi
          </span>
        </div>
      </div>

      {/* Main Navbar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Portal Title */}
          <Link 
            to="/inspector-home" 
            className="flex items-center gap-3 group focus:outline-none"
            onClick={() => setMobileMenuOpen(false)}
          >
            <div className="w-9 h-9 rounded-md bg-[#061a2e] text-brand-cream flex items-center justify-center border border-brand-sage/40 shadow-sm">
              <ShieldCheck className="w-5 h-5 text-brand-cream" />
            </div>

            <div>
              <div className="flex items-center gap-2">
                <span className="text-base sm:text-lg font-bold tracking-tight text-white">
                  NiyamDrishti <span className="text-brand-cream">AI</span>
                </span>
                <span className="bg-[#061a2e] text-brand-cream text-[10px] font-bold px-1.5 py-0.5 rounded border border-brand-sage/30 uppercase tracking-widest font-mono">
                  SIH Prototype
                </span>
              </div>
              <p className="text-[11px] text-slate-300 font-medium">
                Legal Metrology (Packaged Commodities) Rules, 2011
              </p>
            </div>
          </Link>

          {!isLoginPage && (
            <>
              {/* Desktop Nav Links */}
              <nav className="hidden md:flex items-center gap-1.5">
                {navLinks.map((item) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      className={`flex items-center gap-2 px-3 py-2 rounded-md text-xs font-semibold tracking-wide transition-colors ${
                        isActive
                          ? 'bg-[#061a2e] text-brand-cream border border-brand-sage/40 shadow-sm'
                          : 'text-slate-200 hover:text-white hover:bg-[#061a2e]/60'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span>{item.name}</span>
                    </Link>
                  );
                })}
              </nav>

              {/* Officer Profile & Sign Out (Desktop) */}
              <div className="hidden lg:flex items-center gap-3 pl-4 border-l border-white/10">
                <div className="text-right">
                  <div className="text-xs font-bold text-white">{OFFICER_PROFILE.name}</div>
                  <div className="text-[10px] font-mono text-brand-cream">{OFFICER_PROFILE.badgeId}</div>
                </div>
                {/* Secondary icon using brand-bronze */}
                <div className="w-8 h-8 rounded-md bg-brand-bronze border border-brand-cream/30 flex items-center justify-center text-white font-bold text-xs shadow-sm">
                  RS
                </div>
                <button
                  onClick={() => navigate('/login')}
                  title="Sign Out"
                  className="p-1.5 text-slate-300 hover:text-red-400 hover:bg-[#061a2e] rounded-md transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>

              {/* Mobile Menu Button */}
              <div className="flex md:hidden items-center gap-2">
                <Link
                  to="/guided-scan"
                  className="bg-[#061a2e] hover:bg-[#051424] text-brand-cream border border-brand-sage/40 px-2.5 py-1.5 rounded-md text-xs font-semibold flex items-center gap-1 shadow-sm"
                >
                  <Camera className="w-3.5 h-3.5 text-brand-cream" />
                  <span>Scan</span>
                </Link>
                <button
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="p-2 text-slate-300 hover:text-white hover:bg-[#061a2e] rounded-md focus:outline-none"
                  aria-label="Toggle navigation menu"
                >
                  {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              </div>
            </>
          )}

          {isLoginPage && (
            <div className="flex items-center gap-2 text-xs text-brand-cream font-semibold bg-[#061a2e] px-3 py-1.5 rounded-md border border-brand-sage/30 font-mono">
              <UserCheck className="w-4 h-4 text-brand-cream" />
              <span>Authorised Officer Sign-in</span>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {!isLoginPage && mobileMenuOpen && (
        <div className="md:hidden bg-[#061a2e] border-b border-brand-navy px-4 pt-2 pb-4 space-y-2">
          <div className="p-3 bg-brand-navy rounded-md border border-brand-sage/30 mb-2 flex items-center justify-between">
            <div>
              <p className="text-xs font-bold text-white">{OFFICER_PROFILE.name}</p>
              <p className="text-[11px] text-brand-cream font-mono">{OFFICER_PROFILE.badgeId}</p>
              <p className="text-[10px] text-slate-300">{OFFICER_PROFILE.zone}</p>
            </div>
            {/* Secondary bronze icon */}
            <div className="w-8 h-8 rounded-md bg-brand-bronze text-white flex items-center justify-center font-bold text-xs">
              RS
            </div>
          </div>

          {navLinks.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={() => setMobileMenuOpen(false)}
                className={`flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium ${
                  isActive
                    ? 'bg-brand-navy text-brand-cream font-semibold border border-brand-sage/30'
                    : 'text-slate-200 hover:bg-brand-navy'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.name}</span>
                </div>
                <ChevronRight className="w-4 h-4 text-slate-400" />
              </Link>
            );
          })}

          <button
            onClick={() => {
              setMobileMenuOpen(false);
              navigate('/login');
            }}
            className="w-full mt-2 flex items-center justify-center gap-2 px-3 py-2 rounded-md text-sm text-red-300 hover:bg-brand-navy border border-red-900/40 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Sign Out Terminal</span>
          </button>
        </div>
      )}
    </header>
  );
}
