import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { MapPin, X } from 'lucide-react';

export default function MapPanel({ markets = [], farmerLocation = null, onMarketClick }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    // Mapbox or Leaflet implementation
    // For demo, showing a simple div with market list
    // In production, integrate with mapbox-gl or Leaflet

    if (mapContainer.current) {
      setMapLoaded(true);
    }
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="card col-span-1 md:col-span-2 h-96 relative overflow-hidden"
    >
      <h3 className="card-title mb-4 absolute top-6 left-6 z-10">Market Locations</h3>

      <div
        ref={mapContainer}
        className="w-full h-full bg-gradient-to-br from-surface-dark to-[#1a2a47] relative"
      >
        {/* Map placeholder with gradient background */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-900/10 via-transparent to-purple-900/10" />

        {/* Market Markers (mock) */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="space-y-2 max-h-full overflow-y-auto">
            {markets.length > 0 ? (
              markets.map((market, idx) => (
                <motion.button
                  key={market.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  onClick={() => onMarketClick?.(market)}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-surface-light border border-border-default hover:border-primary-600 transition-all group"
                >
                  <MapPin className="w-4 h-4 text-accent flex-shrink-0" />
                  <div className="text-left text-sm">
                    <div className="font-medium text-text-primary group-hover:text-primary-600">
                      {market.name}
                    </div>
                    <div className="text-xs text-text-muted">
                      {market.distance_km} km • KES {market.latest_price}
                    </div>
                  </div>
                </motion.button>
              ))
            ) : (
              <div className="text-center text-text-muted">
                <p>No markets available</p>
              </div>
            )}
          </div>
        </div>

        {/* Info Box */}
        <div className="absolute bottom-4 right-4 bg-surface-light border border-border-default rounded-lg p-3 text-xs text-text-muted max-w-xs z-10">
          <p>
            <strong>Tip:</strong> Click on a market to see details and request logistics recommendation.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
