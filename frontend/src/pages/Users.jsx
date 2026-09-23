import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import api from '../api';
import { Loader2, UserX, UserCheck, Shield } from 'lucide-react';

export default function Users() {
  const { user: currentUser } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchUsers = async () => {
    try {
      const res = await api.get('/users');
      // Admin sees users, Super Admin sees all. The backend already handles filtering, 
      // but let's just filter for normal USERs if this is the "Users" page.
      setUsers(res.data.filter(u => u.role === 'USER'));
    } catch (err) {
      console.error(err);
      setError("Failed to fetch users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const toggleStatus = async (user) => {
    try {
      await api.patch(`/users/${user.id}`, { is_active: !user.is_active });
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Failed to update user");
    }
  };

  if (loading) return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin text-accent" /></div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="animate-fade-in pb-10">
      <header className="mb-10">
        <h1 className="text-3xl font-black text-textMain mb-2">Manage Users</h1>
        <p className="text-text2">View and manage normal user accounts in FlowForge.</p>
      </header>

      <div className="bg-bg2 border border-border rounded-2xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-bg3 border-b border-border">
                <th className="p-4 font-bold text-textMain text-sm">User</th>
                <th className="p-4 font-bold text-textMain text-sm">Email</th>
                <th className="p-4 font-bold text-textMain text-sm">Status</th>
                <th className="p-4 font-bold text-textMain text-sm">Joined</th>
                <th className="p-4 font-bold text-textMain text-sm text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b border-border hover:bg-bg3/50 transition-colors">
                  <td className="p-4 flex items-center gap-3">
                    <img 
                      src={u.avatar_url ? `http://localhost:8000${u.avatar_url}` : `https://ui-avatars.com/api/?name=${u.first_name}+${u.last_name}&background=6c5ce7&color=fff`} 
                      alt="avatar" 
                      className="w-10 h-10 rounded-full object-cover"
                    />
                    <div>
                      <div className="font-semibold text-textMain">{u.first_name} {u.last_name}</div>
                      <div className="text-xs text-text3 flex items-center gap-1 mt-0.5">
                        <Shield size={12} className="text-blue-400" /> {u.role}
                      </div>
                    </div>
                  </td>
                  <td className="p-4 text-text2 text-sm">{u.email}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold ${u.is_active ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'}`}>
                      {u.is_active ? 'Active' : 'Deactivated'}
                    </span>
                  </td>
                  <td className="p-4 text-text3 text-sm">
                    {new Date(u.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-4 text-right">
                    <button 
                      onClick={() => toggleStatus(u)} 
                      className={`p-2 rounded-lg transition-colors ${u.is_active ? 'bg-red-500/10 text-red-500 hover:bg-red-500/20' : 'bg-green-500/10 text-green-500 hover:bg-green-500/20'}`}
                      title={u.is_active ? "Deactivate User" : "Activate User"}
                    >
                      {u.is_active ? <UserX size={18} /> : <UserCheck size={18} />}
                    </button>
                  </td>
                </tr>
              ))}
              {users.length === 0 && (
                <tr>
                  <td colSpan="5" className="p-8 text-center text-text3">No users found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
