import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import LogisticsCard from './components/LogisticsCard';
import LogisticsModal from './components/LogisticsModal';
import ErrorBanner from './components/ErrorBanner';
import LoadingSpinner from './components/LoadingSpinner';
import { getMarkets, createShipment } from './lib/apiClient';
import Signup from './auth/Signup';
import Signin from './auth/Signin';
import Dashboard from './auth/Dashboard';
import Logistics from './auth/Logistics';
import { demoFarmer, mockMarkets } from './lib/constants';
import './index.css';

export default function App() {
  const [markets, setMarkets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [farmer, setFarmer] = useState(demoFarmer);
  const [modalOpen, setModalOpen] = useState(false);
  const [creatingShipment, setCreatingShipment] = useState(false);

  useEffect(() => {
    const loadMarkets = async () => {
      try {
        setLoading(true);
        const data = await getMarkets();
        setMarkets(data.markets || mockMarkets);
        setError(null);
      } catch (e) {
        console.error('Failed to load markets:', e);
        setMarkets(mockMarkets);
        setError('Using cached market data');
      } finally {
        setLoading(false);
      }
    };

    loadMarkets();
  }, []);

  const handleCreateShipment = async (plan) => {
    setSelectedPlan(plan);
    setModalOpen(true);
  };

  const handleConfirmShipment = async () => {
    setCreatingShipment(true);
    try {
      const payload = {
        market: selectedPlan.best_market_location,
        transport_mode: selectedPlan.transport_mode,
        cost: selectedPlan.transport_cost_kes,
        sacks: farmer.quantity_sacks,
        farmer_id: farmer.id,
      };
      await createShipment(payload);
      setError(null);
      setModalOpen(false);
      // Show success message
      setTimeout(() => {
        alert('Shipment created successfully!');
        setSelectedPlan(null);
      }, 500);
    } catch (e) {
      setError(`Failed to create shipment: ${e.message}`);
    } finally {
      setCreatingShipment(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
            🌾 SPROUT AI
          </h1>
          <p className="text-slate-400 text-sm mt-1">Agricultural Market Intelligence</p>
        </div>
      </header>

      {/* Main Content */}
      <BrowserRouter>
        <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex gap-2 mb-6">
            <Link to="/" className="px-3 py-1 bg-slate-700 rounded">Home</Link>
            <Link to="/signup" className="px-3 py-1 bg-slate-700 rounded">Sign Up</Link>
            <Link to="/signin" className="px-3 py-1 bg-slate-700 rounded">Sign In</Link>
            <Link to="/dashboard" className="px-3 py-1 bg-slate-700 rounded">Dashboard</Link>
            <Link to="/logistics" className="px-3 py-1 bg-slate-700 rounded">Logistics</Link>
          </div>

          <Routes>
            <Route path="/" element={
              <div className="py-24">
                <div className="max-w-4xl mx-auto text-center">
                  <h2 className="text-6xl font-extrabold leading-tight">Sprout AI</h2>
                  <p className="mt-6 text-2xl text-slate-300">AI-powered market &amp; transport intelligence for smallholder farmers.</p>
                </div>
              </div>
            } />

            <Route path="/signup" element={<Signup onSuccess={(jobId) => { if (jobId) localStorage.setItem('last_job_id', jobId); window.location.href = '/dashboard'; }} />} />
            <Route path="/signin" element={<Signin />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/logistics" element={<Logistics />} />
          </Routes>
        </main>
      </BrowserRouter>

      {/* Modal */}
      <AnimatePresence>
        {modalOpen && (
          <LogisticsModal
            plan={selectedPlan}
            farmer={farmer}
            onConfirm={handleConfirmShipment}
            onCancel={() => setModalOpen(false)}
            loading={creatingShipment}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
