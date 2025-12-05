import React, { useEffect, useState, useRef } from 'react';
import { getPrediction, predictMarket } from '../lib/apiClient';
import LoadingSpinner from '../components/LoadingSpinner';

const COUNTIES = ["Kajiado", "Narok", "Nakuru", "Nyandarua", "Transnzoia"];
const SUBCOUNTIES = {
  Kajiado: ["Loitokitok", "Kajiado North", "Kajiado West"],
  Narok: ["Narok North", "Narok South"],
  Nakuru: ["Nakuru East", "Nakuru West"],
  Nyandarua: ["Ol Kalou", "Kinangop"],
  Transnzoia: ["Kitale", "Kwanza"]
};

const PRODUCE = ["maize", "beans", "onions", "wheat"];

export default function Dashboard() {
  const [jobId, setJobId] = useState(() => localStorage.getItem('last_job_id'));
  const [loading, setLoading] = useState(!!jobId);
  const [prediction, setPrediction] = useState(() => {
    const raw = localStorage.getItem('last_prediction');
    return raw ? JSON.parse(raw) : null;
  });
  const [error, setError] = useState(null);
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('job_history') || '[]');
    } catch (e) {
      return [];
    }
  });
  const attemptsRef = useRef(0);
  const maxAttempts = 40; // longer polling window

  const [form, setForm] = useState({
    produce: prediction?.produce || PRODUCE[0],
    quantity: prediction?.quantity || 100,
    county: prediction?.location || COUNTIES[0],
    subcounty: prediction?.subcounty || (SUBCOUNTIES[COUNTIES[0]][0] || '')
  });

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      if (!jobId) {
        setError(null);
        setLoading(false);
        return;
      }

      try {
        attemptsRef.current = 0;

        while (!cancelled && attemptsRef.current < maxAttempts) {
          attemptsRef.current += 1;
          try {
            const res = await getPrediction(jobId);
            if (res) {
              setPrediction(res);
              setLoading(false);
              setError(null);
              localStorage.setItem('last_prediction', JSON.stringify(res));
              return;
            }
          } catch (err) {
            if (err && err.status && err.status !== 404) {
              setError(err.message || String(err));
              setLoading(false);
              return;
            }
          }

          await new Promise(r => setTimeout(r, 500));
        }

        if (!prediction && !cancelled) {
          setError('Prediction not available yet. Try refreshing.');
          setLoading(false);
        }
      } catch (e) {
        if (!cancelled) {
          setError(String(e));
          setLoading(false);
        }
      }
    }

    poll();

    return () => { cancelled = true; };
  }, [jobId]);

  function refresh() {
    setLoading(true);
    setError(null);
    setPrediction(null);
    // bump jobId to re-trigger effect
    setJobId(localStorage.getItem('last_job_id'));
  }

  function onFormChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
    if (name === 'county') {
      setForm(prev => ({ ...prev, subcounty: SUBCOUNTIES[value][0] || '' }));
    }
  }

  async function submitPrediction(e) {
    e && e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        produce: form.produce,
        quantity: Number(form.quantity),
        location: form.county,
        transport_mode: 'pickup',
        has_storage: false
      };

      const res = await predictMarket(payload);
      // backend returns prediction extended with job_id (PredictionJobResponse)
      const newJobId = res.job_id || res.jobId || res.jobid;
      if (newJobId) {
        localStorage.setItem('last_job_id', newJobId);
        setJobId(newJobId);

        // update history
        const entry = { jobId: newJobId, ts: Date.now(), produce: payload.produce, quantity: payload.quantity, location: payload.location };
        const next = [entry, ...history].slice(0, 50);
        setHistory(next);
        localStorage.setItem('job_history', JSON.stringify(next));
      }
    } catch (err) {
      setError(err.message || String(err));
      setLoading(false);
    }
  }

  function loadFromHistory(entry) {
    if (!entry || !entry.jobId) return;
    localStorage.setItem('last_job_id', entry.jobId);
    setJobId(entry.jobId);
    setLoading(true);
    setPrediction(null);
  }

  return (
    <div className="max-w-5xl mx-auto p-6 bg-white/5 rounded">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left: editable inputs + history */}
        <div className="col-span-1 bg-white/80 p-4 rounded text-slate-900">
          <h3 className="text-lg font-semibold mb-3">Your crop & location</h3>
          <form onSubmit={submitPrediction} className="space-y-3">
            <div>
              <label className="block text-sm text-slate-700">Produce</label>
              <select name="produce" value={form.produce} onChange={onFormChange} className="w-full p-2 rounded text-slate-900 bg-white/90">
                {PRODUCE.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-slate-700">Quantity (kg)</label>
              <input name="quantity" type="number" value={form.quantity} onChange={onFormChange} className="w-full p-2 rounded text-slate-900 bg-white/90" />
            </div>

            <div>
              <label className="block text-sm text-slate-700">County</label>
              <select name="county" value={form.county} onChange={onFormChange} className="w-full p-2 rounded text-slate-900 bg-white/90">
                {COUNTIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-slate-700">Subcounty</label>
              <select name="subcounty" value={form.subcounty} onChange={onFormChange} className="w-full p-2 rounded text-slate-900 bg-white/90">
                {(SUBCOUNTIES[form.county] || []).map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            <div className="flex gap-2">
              <button type="submit" className="flex-1 py-2 bg-cyan-600 text-white rounded">Get Recommendation</button>
              <button type="button" onClick={() => { localStorage.removeItem('last_job_id'); setJobId(null); setPrediction(null); }} className="px-3 py-2 bg-rose-500 text-white rounded">Clear</button>
            </div>
          </form>

          <div className="mt-6">
            <h4 className="text-sm font-semibold mb-2">History</h4>
            {history.length === 0 && <div className="text-sm text-slate-600">No past jobs</div>}
            <ul className="space-y-2 max-h-64 overflow-y-auto">
              {history.map(h => (
                <li key={h.jobId} className="p-2 bg-white rounded shadow-sm flex justify-between items-center text-slate-900">
                  <div>
                    <div className="text-sm font-medium">{h.produce} — {h.quantity}kg</div>
                    <div className="text-xs text-slate-500">{h.location} • {new Date(h.ts).toLocaleString()}</div>
                  </div>
                  <div className="flex flex-col gap-1">
                    <button onClick={() => loadFromHistory(h)} className="text-sm px-2 py-1 bg-slate-200 text-slate-900 rounded">Open</button>
                    <button onClick={() => { const next = history.filter(x => x.jobId !== h.jobId); setHistory(next); localStorage.setItem('job_history', JSON.stringify(next)); }} className="text-sm px-2 py-1 bg-rose-200 text-slate-900 rounded">Delete</button>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Right: prediction */}
        <div className="md:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Dashboard</h2>
            <div className="flex gap-2">
              <button onClick={refresh} className="px-3 py-1 bg-slate-200 text-slate-900 rounded">Refresh</button>
            </div>
          </div>

          {loading && <LoadingSpinner message="Waiting for prediction..." />}

          {error && <div className="mt-3 text-sm text-rose-500">{error}</div>}

          {prediction ? (
            <div className="mt-4 bg-white p-4 rounded shadow">
              <h3 className="text-lg font-semibold text-slate-700">Recommendation</h3>
              <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-800">
                <div>
                  <div className="text-sm text-slate-500">Best market</div>
                  <div className="font-semibold">{prediction.best_market}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Expected price (KES)</div>
                  <div className="font-semibold">{prediction.expected_price}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Transport cost (KES)</div>
                  <div className="font-semibold">{prediction.transport_cost}</div>
                </div>
                <div>
                  <div className="text-sm text-slate-500">Net profit (KES)</div>
                  <div className="font-semibold">{prediction.net_profit}</div>
                </div>
              </div>
              {prediction.recommendation_reason && (
                <div className="mt-3 text-sm text-slate-600">{prediction.recommendation_reason}</div>
              )}
            </div>
          ) : (
            !loading && <div className="text-sm text-slate-600">No prediction loaded. Submit to create one.</div>
          )}
        </div>
      </div>
    </div>
  );
}
