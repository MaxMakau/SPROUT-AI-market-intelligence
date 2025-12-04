import { useState } from 'react';
import { motion } from 'framer-motion';
import { Truck, Car, Bike, RefreshCw } from 'lucide-react';
import { recommendLogistics } from '../lib/apiClient';
import LoadingSpinner from './LoadingSpinner';

function TransportIcon({ mode }) {
  const icons = {
    lorry: <Truck className="w-6 h-6" />,
    pickup: <Car className="w-6 h-6" />,
    motorbike: <Bike className="w-6 h-6" />,
  };
  return icons[mode] || icons.pickup;
}

function getModeColor(mode) {
  const colors = {
    motorbike: { bg: 'bg-purple-900', text: 'text-purple-300' },
    pickup: { bg: 'bg-amber-900', text: 'text-amber-300' },
    lorry: { bg: 'bg-green-900', text: 'text-green-300' },
  };
  return colors[mode] || colors.pickup;
}

export default function LogisticsCard({ farmer, markets, onCreateShipment }) {
  const [loading, setLoading] = useState(false);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);

  async function handleRecommend() {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        quantity_sacks: farmer.quantity_sacks,
        distance_km: farmer.distance_km,
        best_market_location: farmer.best_market_location,
        market_price: farmer.market_price,
      };
      const res = await recommendLogistics(payload);
      setPlan(res);
    } catch (e) {
      setError(e.message || 'Failed to get recommendation');
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="bg-slate-800 border border-slate-700 rounded-lg p-6 shadow-lg"
    >
      <h2 className="text-2xl font-bold text-white mb-2">📦 Get Recommendation</h2>
      <p className="text-slate-400 text-sm mb-6">Optimize your logistics</p>

      {error && (
        <div className="mb-4 p-3 bg-red-900/30 border border-red-700 rounded-lg text-red-200 text-sm">
          ⚠️ {error}
        </div>
      )}

      {loading ? (
        <LoadingSpinner message="Analyzing..." />
      ) : plan ? (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {/* Transport Mode */}
          <div className={`p-4 rounded-lg border-2 ${getModeColor(plan.transport_mode).bg} border-opacity-50`}>
            <div className="flex items-center gap-3 mb-3">
              <div className={`p-2 rounded-lg ${getModeColor(plan.transport_mode).bg}`}>
                <div className={getModeColor(plan.transport_mode).text}>
                  <TransportIcon mode={plan.transport_mode} />
                </div>
              </div>
              <div>
                <p className="font-semibold text-white capitalize">{plan.transport_mode}</p>
                <p className="text-sm text-slate-300">Recommended transport method</p>
              </div>
            </div>
          </div>

          {/* Pricing Summary */}
          <div className="grid grid-cols-2 gap-3">
            {/* Transport Cost */}
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-xs text-slate-400 mb-1">Transport Cost</p>
              <p className="text-2xl font-bold text-cyan-400">{plan.transport_cost_kes}sh</p>
              <p className="text-xs text-slate-400 mt-1">({plan.transport_cost_kes / farmer.quantity_sacks}sh/sack)</p>
            </div>

            {/* Market Price */}
            <div className="bg-slate-700 rounded-lg p-4">
              <p className="text-xs text-slate-400 mb-1">Market Price</p>
              <p className="text-2xl font-bold text-green-400">{plan.market_price}sh/kg</p>
              <p className="text-xs text-slate-400 mt-1">per kilogram</p>
            </div>
          </div>

          {/* Details */}
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="bg-slate-700 rounded-lg p-3">
              <p className="text-slate-400">Distance</p>
              <p className="font-semibold text-white text-lg">{plan.distance_km}km</p>
            </div>
            <div className="bg-slate-700 rounded-lg p-3">
              <p className="text-slate-400">Quantity</p>
              <p className="font-semibold text-white text-lg">{farmer.quantity_sacks} sacks</p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              onClick={() => onCreateShipment?.(plan)}
              className="flex-1 bg-cyan-600 hover:bg-cyan-700 text-white font-semibold py-2 px-4 rounded-lg transition"
            >
              Create Shipment
            </button>
            <button
              onClick={handleRecommend}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </motion.div>
      ) : (
        <button
          onClick={handleRecommend}
          disabled={loading}
          className="w-full bg-cyan-600 hover:bg-cyan-700 text-white font-bold py-3 px-4 rounded-lg transition"
        >
          🚚 Get Recommendation
        </button>
      )}
    </motion.div>
  );
}
