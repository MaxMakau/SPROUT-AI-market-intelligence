import { motion } from 'framer-motion';
import { X, Check } from 'lucide-react';

export default function LogisticsModal({ plan, farmer, onConfirm, onCancel, loading = false }) {
  // Calculate ETA (mock: avg speed 60km/h)
  const etaHours = Math.floor(farmer.distance_km / 60);
  const etaMinutes = Math.round((farmer.distance_km % 60 / 60) * 60);

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        className="bg-slate-800 border border-slate-700 rounded-lg shadow-2xl max-w-md w-full"
        role="dialog"
        aria-labelledby="modal-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 id="modal-title" className="text-xl font-bold text-white">
            ✅ Confirm Shipment
          </h2>
          <button
            onClick={onCancel}
            className="p-1 hover:bg-slate-700 rounded-lg transition"
            aria-label="Close modal"
          >
            <X className="w-5 h-5 text-slate-400" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          {/* Summary */}
          <div className="bg-slate-700 rounded-lg p-4 space-y-3">
            <h3 className="text-sm font-semibold text-cyan-400 uppercase">Shipment Details</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-300">Quantity:</span>
                <span className="font-semibold text-white">{farmer.quantity_sacks} sacks</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Destination:</span>
                <span className="font-semibold text-white text-right">{plan.best_market_location}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Transport:</span>
                <span className="font-semibold text-white capitalize">{plan.transport_mode}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Distance:</span>
                <span className="font-semibold text-white">{plan.distance_km}km</span>
              </div>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div className="bg-slate-700 rounded-lg p-4 space-y-3">
            <h3 className="text-sm font-semibold text-green-400 uppercase">Pricing</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-300">Transport Cost:</span>
                <span className="font-semibold text-white">{plan.transport_cost_kes}sh total</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-300">Per Sack:</span>
                <span className="font-semibold text-cyan-300">{plan.transport_cost_kes / farmer.quantity_sacks}sh</span>
              </div>
              <div className="pt-2 border-t border-slate-600 flex justify-between">
                <span className="text-slate-300">Market Price:</span>
                <span className="font-semibold text-green-400">{plan.market_price}sh/kg</span>
              </div>
            </div>
          </div>

          {/* ETA */}
          <div className="bg-blue-900/30 border border-blue-700 rounded-lg p-4">
            <p className="text-sm text-blue-300">
              ⏱️ Estimated arrival: <span className="font-semibold">{etaHours}h {etaMinutes}m</span>
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 p-6 border-t border-slate-700">
          <button
            onClick={onCancel}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <span className="animate-spin">⏳</span>
            ) : (
              <>
                <Check className="w-4 h-4" />
                Create
              </>
            )}
          </button>
        </div>
      </motion.div>
    </div>
  );
}
