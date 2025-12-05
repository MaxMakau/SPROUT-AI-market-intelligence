import React, { useState } from 'react';
import { signin } from '../lib/apiClient';

export default function Signin() {
  const [form, setForm] = useState({ phone: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  function onChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: value }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    try {
      const res = await signin({ phone: form.phone, password: form.password });
      if (res && res.success) {
        if (res.user_id) localStorage.setItem('user_id', res.user_id);
        setMessage(res.message || 'Signed in');
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
      <h2 className="text-xl font-semibold mb-4">Sign In</h2>
      {message && <div className="mb-3 text-sm text-cyan-200">{message}</div>}
      <form onSubmit={onSubmit} className="space-y-3">
        <input name="phone" value={form.phone} onChange={onChange} placeholder="Phone (+2547...)" className="w-full p-2 rounded bg-slate-800" />
        <input name="password" value={form.password} onChange={onChange} placeholder="Password" type="password" className="w-full p-2 rounded bg-slate-800" />

        <button disabled={loading} className="w-full py-2 bg-cyan-500 rounded text-slate-900 font-semibold">
          {loading ? 'Signing in...' : 'Sign In'}
        </button>
      </form>
    </div>
  );
}
