import React, { useEffect, useState } from 'react';
import { getLogistics, createShipment } from '../lib/apiClient';
import LoadingSpinner from '../components/LoadingSpinner';

export default function Logistics() {
  const [jobId, setJobId] = useState(() => localStorage.getItem('last_job_id'));
  const [loading, setLoading] = useState(!!jobId);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [creating, setCreating] = useState(false);

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
    if (!data) return;
    setCreating(true);
    try {
      // Build a minimal shipment payload from logistics data
      const payload = {
        market: data.best_market,
        transport_mode: 'pickup',
        cost: data.transport_cost,
        quantity: data.quantity,
        job_id: jobId,
      };

      await createShipment(payload);
      alert('Shipment request submitted (scaffold).');
    } catch (err) {
      alert('Failed to create shipment: ' + (err.message || String(err)));
    } finally {
      setCreating(false);
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
              <div className="font-semibold">{data.transport_cost}</div>
            </div>
          </div>

          <div className="mt-4 flex gap-2">
            <button onClick={handleCreateShipment} disabled={creating} className="px-4 py-2 bg-cyan-500 rounded text-slate-900">
              {creating ? 'Requesting...' : 'Need Transport'}
            </button>
            <button onClick={() => { localStorage.removeItem('last_job_id'); setJobId(null); setData(null); }} className="px-4 py-2 bg-rose-600 rounded">
              Clear Job
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
