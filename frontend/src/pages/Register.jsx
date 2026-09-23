import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api';
import { AuthContext } from '../contexts/AuthContext';

export default function Register() {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await api.post('/auth/register', formData);
      
      // Auto login after register
      const params = new URLSearchParams();
      params.append('username', formData.email);
      params.append('password', formData.password);
      
      const res = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const token = res.data.access_token;
      const userRes = await api.get('/auth/me', { headers: { Authorization: `Bearer ${token}` } });
      
      login(token, userRes.data);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[radial-gradient(ellipse_60%_50%_at_50%_10%,rgba(108,92,231,0.12),transparent_60%),var(--bg)] p-6">
      <div className="w-full max-w-md bg-bg2 border border-border rounded-2xl p-8 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
        <div className="text-center mb-8">
          <div className="text-accent2 font-black text-sm uppercase tracking-widest mb-2">FlowForge</div>
          <h1 className="text-2xl font-bold text-textMain mb-1">Create an account</h1>
          <p className="text-text2 text-sm">Join us to start managing your projects.</p>
        </div>

        {error && <div className="bg-red/10 border border-red/20 text-red px-4 py-3 rounded-lg text-sm mb-4">{error}</div>}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-text2 mb-1.5">First Name</label>
              <input type="text" required value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:outline-none focus:border-accent" />
            </div>
            <div>
              <label className="block text-sm font-semibold text-text2 mb-1.5">Last Name</label>
              <input type="text" required value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:outline-none focus:border-accent" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-semibold text-text2 mb-1.5">Email</label>
            <input type="email" required value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:outline-none focus:border-accent" />
          </div>
          <div>
            <label className="block text-sm font-semibold text-text2 mb-1.5">Password</label>
            <input type="password" required minLength={8} value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:outline-none focus:border-accent" />
          </div>
          <button type="submit" className="w-full bg-accent hover:bg-[#5b4cdb] text-white font-semibold py-2.5 rounded-lg transition-all shadow-[0_0_20px_rgba(108,92,231,0.4)] mt-2">
            Sign Up
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-text3">
          Already have an account? <Link to="/login" className="text-accent2 hover:text-accent font-medium">Log in</Link>
        </div>
      </div>
    </div>
  );
}
