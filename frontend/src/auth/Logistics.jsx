import React, { useEffect, useState } from 'react';
import { getLogistics, createShipment, getDetailedLogistics, recommendLogistics } from '../lib/apiClient';
import { computeTransportCostDetailed } from '../lib/logistics';
import { mockMarkets } from '../lib/constants';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Logistics() {
  const [jobId, setJobId] = useState(() => localStorage.getItem('last_job_id'));
  const [loading, setLoading] = useState(!!jobId);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [creating, setCreating] = useState(false);
  const [shipmentResult, setShipmentResult] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [recLoading, setRecLoading] = useState(false);
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduledDate, setScheduledDate] = useState(() => {
    const d = new Date();
    return d.toISOString().slice(0, 10);
  });
  const [priceEstimatedWarning, setPriceEstimatedWarning] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!jobId) {
        setError('No job id available.');
        setLoading(false);
        return;
      }
      try {
        const res = await getLogistics(jobId);
        if (!cancelled) {
          setData(res);
          // Try to fetch detailed breakdown from logistics module
          try {
            const details = await getDetailedLogistics(jobId);
            if (!cancelled) setData(d => ({ ...(d || {}), _detailed: details }));
          } catch (e) {
            // If detailed call fails, compute locally when possible
            if (!cancelled && res && res.quantity) {
              const local = computeTransportCostDetailed(res.quantity * 1, res.distance_km || 0);
              setData(d => ({ ...(d || {}), _detailed: local }));
            }
          }
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || String(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [jobId]);

  async function handleCreateShipment() {
    // Create shipment only after recommendation available
    if (!recommendation && !data) return;
    setCreating(true);
    try {
      const plan = recommendation || {
        transport_mode: data.transport_mode || 'pickup',
        transport_cost_kes: data.transport_cost || 0,
        distance_km: data.distance_km || 0,
        best_market_location: data.best_market || data.best_market_location || 'Unknown',
        market_price: data.market_price || 0,
      };

      const payload = {
        market: plan.best_market_location || plan.best_market || data.best_market,
        transport_mode: plan.transport_mode,
        cost: plan.transport_cost_kes || plan.total_cost || 0,
        sacks: Math.max(1, Math.round((data?.quantity || 0) / 90)),
        job_id: jobId,
      };

      const res = await createShipment(payload);
      setShipmentResult(res);
      setError(null);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setCreating(false);
    }
  }

  async function handleGetRecommendation() {
    if (!data) {
      setError('No logistics data available to recommend.');
      return;
    }
    setRecLoading(true);
    setError(null);
    try {
      const qty_sacks = Math.max(1, Math.round((data.quantity || 0) / 90));
      const bestMarketName = data.best_market || data.best_market_location || null;

      // Try to determine a positive market_price from available fields or mockMarkets
      let marketPrice = data.market_price || data.expected_price || null;
      setPriceEstimatedWarning(null);

      if ((!marketPrice || marketPrice <= 0) && bestMarketName) {
        // Try exact match first
        let found = mockMarkets.find(m => m.name === bestMarketName || m.id === bestMarketName);
        // Try fuzzy match (case-insensitive includes)
        if (!found) {
          const nameLower = bestMarketName.toLowerCase();
          found = mockMarkets.find(m => (m.name || '').toLowerCase().includes(nameLower) || (m.id || '').toLowerCase().includes(nameLower));
        }
        if (found && found.latest_price) {
          marketPrice = found.latest_price;
          setPriceEstimatedWarning(`Market price not present in prediction — using ${marketPrice} from local market data (${found.name}).`);
        }
      }

      // Final fallback: use average price across mockMarkets if still missing
      if (!marketPrice || marketPrice <= 0) {
        const prices = mockMarkets.map(m => m.latest_price).filter(Boolean);
        if (prices.length > 0) {
          const avg = Math.round(prices.reduce((a, b) => a + b, 0) / prices.length);
          marketPrice = avg;
          setPriceEstimatedWarning(`Market price missing — using estimated average price ${marketPrice} from sample markets.`);
        }
      }

      if (!marketPrice || marketPrice <= 0) {
        setError('Unable to determine market price for recommendation. Please ensure the prediction includes a market price.');
        setRecLoading(false);
        return;
      }

      const payload = {
        quantity_sacks: qty_sacks,
        distance_km: data.distance_km || 0,
        best_market_location: bestMarketName || 'Unknown',
        market_price: marketPrice,
      };

      const res = await recommendLogistics(payload);
      // The backend returns a LogisticsResponse-shaped object
      setRecommendation(res);
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setRecLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white/5 rounded">
      <h2 className="text-xl font-semibold mb-4">Logistics</h2>

      {!jobId && <div className="text-sm text-slate-300 mb-3">No job id found. Trigger a prediction first.</div>}

      {loading && <LoadingSpinner message="Loading logistics..." />}

      {error && <div className="text-rose-400 mb-3">{error}</div>}

      {data && (
        <div className="bg-slate-800 p-4 rounded">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <div className="text-sm text-slate-400">Produce</div>
              <div className="font-semibold">{data.produce}</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">Quantity (kg)</div>
              <div className="font-semibold">{data.quantity}</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">Best market</div>
              <div className="font-semibold">{data.best_market}</div>
            </div>
            <div>
              <div className="text-sm text-slate-400">Transport cost (KES)</div>
              <div className="font-semibold">{data.transport_cost ?? data.transport_cost_kes ?? (data._detailed ? data._detailed.total_cost : '—')}</div>
            </div>
          </div>

          <div className="mt-4">
            {!recommendation ? (
              <div className="flex gap-2">
                <button onClick={handleGetRecommendation} disabled={recLoading} className="px-4 py-2 bg-cyan-500 rounded text-slate-900">
                  {recLoading ? 'Analyzing...' : 'Need Transport'}
                </button>
                <button onClick={() => { localStorage.removeItem('last_job_id'); setJobId(null); setData(null); }} className="px-4 py-2 bg-rose-600 rounded">
                  Clear Job
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="p-3 bg-slate-700 rounded grid grid-cols-1 sm:grid-cols-2 gap-3">
                  <div>
                    <div className="text-sm text-slate-400">Recommended transport</div>
                    <div className="font-semibold capitalize">{recommendation.transport_mode}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">Estimated cost (KES)</div>
                    <div className="font-semibold">{recommendation.transport_cost_kes}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">Distance (km)</div>
                    <div className="font-semibold">{recommendation.distance_km}</div>
                  </div>
                  <div>
                    <div className="text-sm text-slate-400">Market price</div>
                    <div className="font-semibold">{recommendation.market_price ?? '—'}</div>
                  </div>
                </div>

                <div className="space-y-3">
                  {!showSchedule ? (
                    <div className="flex gap-2">
                      <button onClick={() => setShowSchedule(true)} disabled={creating} className="px-4 py-2 bg-green-600 rounded text-white">
                        Create Shipment
                      </button>
                      <button onClick={() => setRecommendation(null)} className="px-4 py-2 bg-slate-600 rounded text-white">Cancel</button>
                    </div>
                  ) : (
                    <div className="p-3 bg-slate-700 rounded grid grid-cols-1 sm:grid-cols-3 gap-3 items-end">
                      <div className="col-span-2">
                        <label className="block text-sm text-slate-400">Schedule transport date</label>
                        <input
                          type="date"
                          value={scheduledDate}
                          min={new Date().toISOString().slice(0, 10)}
                          onChange={(e) => setScheduledDate(e.target.value)}
                          className="mt-1 w-full p-2 rounded text-slate-900 bg-white/90"
                        />
                      </div>
                      <div className="flex gap-2">
                        <button onClick={async () => {
                          // Mock create shipment: do not send to DB, just show success
                          setCreating(true);
                          try {
                            // simulate delay
                            await new Promise(r => setTimeout(r, 600));
                            const mockId = `mock_${Date.now().toString(36)}`;
                            setShipmentResult({ shipment_id: mockId, scheduled_date: scheduledDate });
                            setError(null);
                            setRecommendation(null);
                            setShowSchedule(false);
                          } finally {
                            setCreating(false);
                          }
                        }} className="px-4 py-2 bg-green-600 rounded text-white">Confirm</button>
                        <button onClick={() => setShowSchedule(false)} className="px-4 py-2 bg-slate-600 rounded text-white">Cancel</button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          {shipmentResult && (
            <div className="mt-4 p-3 bg-green-900/30 border border-green-800 rounded text-green-100">
              Shipment scheduled successfully for <span className="font-semibold ml-2">{shipmentResult.scheduled_date}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
