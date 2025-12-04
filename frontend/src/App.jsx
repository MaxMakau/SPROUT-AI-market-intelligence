import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import LogisticsCard from './components/LogisticsCard';
import LogisticsModal from './components/LogisticsModal';
import ErrorBanner from './components/ErrorBanner';
import LoadingSpinner from './components/LoadingSpinner';
import { getMarkets, createShipment } from './lib/apiClient';
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
            🌾 SPROUT Logistics
          </h1>
          <p className="text-slate-400 text-sm mt-1">Agricultural Market Intelligence</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <ErrorBanner
            message={error}
            onDismiss={() => setError(null)}
            type="warning"
          />
        )}

        {loading ? (
          <LoadingSpinner message="Loading markets..." />
        ) : (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-8"
          >
            {/* Left: Logistics Recommendation */}
            <div className="lg:col-span-2">
              <LogisticsCard
                farmer={farmer}
                markets={markets}
                onCreateShipment={handleCreateShipment}
              />
            </div>

            {/* Right: Markets Quick View */}
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-lg"
            >
              <h3 className="text-lg font-semibold mb-4 text-cyan-400">Available Markets</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {markets.slice(0, 8).map((market) => (
                  <motion.div
                    key={market.id}
                    whileHover={{ x: 4 }}
                    onClick={() => {
                      setFarmer(prev => ({
                        ...prev,
                        best_market_location: market.name,
                        distance_km: market.distance_km,
                        market_price: market.latest_price,
                      }));
                    }}
                    className="p-3 bg-slate-700 rounded-lg cursor-pointer hover:bg-slate-600 transition"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="font-medium text-white text-sm">{market.name}</p>
                        <p className="text-slate-400 text-xs mt-1">📍 {market.distance_km} km</p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold text-cyan-400 text-sm">{market.latest_price}sh/kg</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </main>

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
