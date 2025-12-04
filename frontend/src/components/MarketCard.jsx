import { motion } from 'framer-motion';
import { MapPin, TrendingUp } from 'lucide-react';

export default function MarketCard({ market, onSelect }) {
  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-KE', {
      style: 'currency',
      currency: 'KES',
      minimumFractionDigits: 0,
    }).format(value);
  };

  return (
    <motion.button
      onClick={() => onSelect?.(market)}
      whileHover={{ y: -4 }}
      whileTap={{ y: 0 }}
      className="card text-left w-full hover:shadow-lg transition-shadow"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h4 className="font-semibold text-text-primary">{market.name}</h4>
          <div className="flex items-center gap-1 text-text-muted text-xs mt-1">
            <MapPin className="w-3 h-3" />
            {market.distance_km} km away
          </div>
        </div>
        <TrendingUp className="w-4 h-4 text-accent flex-shrink-0" />
      </div>

      <div className="grid grid-cols-2 gap-3 pt-3 border-t border-border-default">
        <div>
          <div className="text-xs text-text-muted mb-1">Current Price</div>
          <div className="font-bold text-text-primary text-lg">
            {formatCurrency(market.latest_price)}
          </div>
        </div>
        <div>
          <div className="text-xs text-text-muted mb-1">Status</div>
          <div className="inline-block px-2 py-1 rounded-full bg-[#065F46] text-[#10B981] text-xs font-medium">
            Available
          </div>
        </div>
      </div>
    </motion.button>
  );
}
