import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Login from './pages/Login';
import InspectorHome from './pages/InspectorHome';
import GuidedScan from './pages/GuidedScan';
import ComplianceResult from './pages/ComplianceResult';
import { MOCK_INSPECTION_DETAIL } from './mockData';

export default function App() {
  const [selectedProduct, setSelectedProduct] = useState(MOCK_INSPECTION_DETAIL);
  const location = useLocation();

  const isLoginPage = location.pathname === '/login';

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-amber-400 selection:text-slate-950">
      {/* Top Government Navigation Bar */}
      <Navbar />

      {/* Main Content Viewport */}
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Navigate to="/inspector-home" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/inspector-home" element={<InspectorHome />} />
          <Route 
            path="/guided-scan" 
            element={<GuidedScan setSelectedProduct={setSelectedProduct} />} 
          />
          <Route 
            path="/compliance-result" 
            element={<ComplianceResult selectedProduct={selectedProduct} />} 
          />
          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/inspector-home" replace />} />
        </Routes>
      </main>

      {/* Official Prototype Footer */}
      {!isLoginPage && <Footer />}
    </div>
  );
}
