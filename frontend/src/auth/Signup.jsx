import React, { useState } from 'react';
import { signup } from '../lib/apiClient';

const COUNTIES = ["Kajiado", "Narok", "Nakuru", "Nyandarua", "Transnzoia"];
const SUBCOUNTIES = {
  Kajiado: ["Loitokitok", "Kajiado North", "Kajiado West"],
  Narok: ["Narok North", "Narok South"],
  Nakuru: ["Nakuru East", "Nakuru West"],
  Nyandarua: ["Ol Kalou", "Kinangop"],
  Transnzoia: ["Kitale", "Kwanza"]
};

const PRODUCE = ["maize", "beans", "onions", "wheat"];

export default function Signup({ onSuccess }) {
  const [form, setForm] = useState({
    name: '',
    phone: '',
    county: COUNTIES[0],
    subcounty: SUBCOUNTIES[COUNTIES[0]][0],
    produce: PRODUCE[0],
    quantity: 0,
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  function onChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

  function onCountyChange(e) {
    const county = e.target.value;
    setForm(prev => ({ ...prev, county, subcounty: SUBCOUNTIES[county][0] }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const payload = {
        name: form.name,
        phone: form.phone,
        county: form.county,
        subcounty: form.subcounty,
        produce: form.produce,
        quantity: Number(form.quantity),
        password: form.password
      };
      const res = await signup(payload);
      if (res && res.success) {
        // store user id and job id for later use
        if (res.user_id) localStorage.setItem('user_id', res.user_id);
        if (res.job_id) localStorage.setItem('last_job_id', res.job_id);
        setMessage(res.message || 'Signed up');
        // navigate to dashboard and let it poll for the job result
        if (typeof onSuccess === 'function') {
          // pass job id (may be undefined) to caller
          onSuccess(res.job_id);
        }
      } else {
        setMessage('Unexpected response');
      }
    } catch (err) {
      setMessage(err.message || String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto p-6 bg-white/5 rounded">
      <h2 className="text-xl font-semibold mb-4">Sign Up</h2>
      {message && <div className="mb-3 text-sm text-cyan-200">{message}</div>}
      <form onSubmit={onSubmit} className="space-y-3">
        <input name="name" value={form.name} onChange={onChange} placeholder="Full name" className="w-full p-2 rounded bg-slate-800" />
        <input name="phone" value={form.phone} onChange={onChange} placeholder="Phone (+2547...)" className="w-full p-2 rounded bg-slate-800" />

        <div className="flex gap-2">
          <select name="county" value={form.county} onChange={onCountyChange} className="flex-1 p-2 rounded bg-slate-800">
            {COUNTIES.map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select name="subcounty" value={form.subcounty} onChange={onChange} className="flex-1 p-2 rounded bg-slate-800">
            {(SUBCOUNTIES[form.county] || []).map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div className="flex gap-2">
          <select name="produce" value={form.produce} onChange={onChange} className="flex-1 p-2 rounded bg-slate-800">
            {PRODUCE.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
          <input name="quantity" value={form.quantity} onChange={onChange} placeholder="Quantity (kg)" type="number" className="flex-1 p-2 rounded bg-slate-800" />
        </div>

        <input name="password" value={form.password} onChange={onChange} placeholder="Password" type="password" className="w-full p-2 rounded bg-slate-800" />

        <button disabled={loading} className="w-full py-2 bg-cyan-500 rounded text-slate-900 font-semibold">
          {loading ? 'Signing up...' : 'Sign Up'}
        </button>
      </form>
    </div>
  );
}
