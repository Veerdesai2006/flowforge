import React, { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../contexts/AuthContext';
import api from '../api';
import { LayoutDashboard, CheckCircle, Clock, ListTodo, Users, UserPlus, Activity, Database, Key } from 'lucide-react';

const StatCard = ({ icon: Icon, title, value, color }) => (
  <div className="bg-bg2 p-6 rounded-2xl border border-border flex items-center gap-4 hover:border-accent2 transition-all group">
    <div className={`p-4 rounded-xl ${color} bg-opacity-10 group-hover:bg-opacity-20 transition-all`}>
      <Icon className={color.replace('bg-', 'text-')} size={24} />
    </div>
    <div>
      <div className="text-text3 text-sm font-medium mb-1">{title}</div>
      <div className="text-3xl font-black text-textMain">{value}</div>
    </div>
  </div>
);

const ActivityFeed = ({ activities }) => {
  if (!activities || activities.length === 0) {
    return <div className="text-text3 text-sm italic">No recent activity.</div>;
  }
  return (
    <div className="space-y-4">
      {activities.map((act) => (
        <div key={act.id} className="flex gap-4 p-4 rounded-xl bg-bg3 border border-border">
          <div className="p-2 bg-accent2/20 text-accent2 rounded-lg h-fit">
            <Activity size={16} />
          </div>
          <div>
            <div className="text-sm font-bold text-textMain">{act.action}</div>
            {act.description && <div className="text-sm text-text2 mt-1">{act.description}</div>}
            <div className="text-xs text-text3 mt-2">{new Date(act.created_at).toLocaleString()}</div>
          </div>
        </div>
      ))}
    </div>
  );
};

const Dashboard = () => {
  const { user } = useContext(AuthContext);
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        let endpoint = '/dashboard/user';
        if (user.role === 'ADMIN') endpoint = '/dashboard/admin';
        if (user.role === 'SUPER_ADMIN') endpoint = '/dashboard/super-admin';
        
        const res = await api.get(endpoint);
        setData(res.data);
      } catch (err) {
        console.error("Dashboard fetch error:", err);
        setError("Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    };
    
    if (user) fetchDashboard();
  }, [user]);

  if (loading) return <div className="p-8 text-center text-text2">Loading dashboard...</div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;
  if (!data) return null;

  return (
    <div className="animate-fade-in pb-10">
      <header className="mb-10">
        <h1 className="text-3xl font-black text-textMain mb-2">Welcome back, {user.first_name} 👋</h1>
        <p className="text-text2">Here's what's happening in your FlowForge workspace.</p>
      </header>

      {/* User Dashboard */}
      {user.role === 'USER' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard icon={Database} title="My Topics" value={data.my_topics} color="bg-blue-500" />
            <StatCard icon={LayoutDashboard} title="My Boards" value={data.my_boards} color="bg-purple-500" />
            <StatCard icon={CheckCircle} title="Completed Tasks" value={data.completed_tasks} color="bg-green-500" />
            <StatCard icon={Clock} title="Running Tasks" value={data.running_tasks} color="bg-accent2" />
          </div>
          
          <div className="bg-bg2 p-6 rounded-2xl border border-border">
            <h2 className="text-xl font-bold text-textMain mb-6 flex items-center gap-2">
              <Activity className="text-accent2" /> My Recent Activity
            </h2>
            <ActivityFeed activities={data.recent_activity} />
          </div>
        </div>
      )}

      {/* Admin Dashboard */}
      {user.role === 'ADMIN' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard icon={Users} title="Total Users" value={data.total_users} color="bg-blue-500" />
            <StatCard icon={CheckCircle} title="Active Users" value={data.active_users} color="bg-green-500" />
            <StatCard icon={Clock} title="Inactive Users" value={data.inactive_users} color="bg-red-500" />
            <StatCard icon={UserPlus} title="Recent Joins" value={data.recent_users} color="bg-accent2" />
          </div>
          
          <div className="bg-bg2 p-6 rounded-2xl border border-border">
            <h2 className="text-xl font-bold text-textMain mb-6 flex items-center gap-2">
              <Activity className="text-accent2" /> System Activity (Users)
            </h2>
            <ActivityFeed activities={data.permitted_activity} />
          </div>
        </div>
      )}

      {/* Super Admin Dashboard */}
      {user.role === 'SUPER_ADMIN' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard icon={Users} title="Total Users" value={data.total_users} color="bg-blue-500" />
            <StatCard icon={Key} title="Total Admins" value={data.total_admins} color="bg-purple-500" />
            <StatCard icon={Key} title="Super Admins" value={data.total_super_admins} color="bg-accent" />
            <StatCard icon={CheckCircle} title="Active Accounts" value={data.active_users} color="bg-green-500" />
          </div>
          
          <div className="bg-bg2 p-6 rounded-2xl border border-border">
            <h2 className="text-xl font-bold text-textMain mb-6 flex items-center gap-2">
              <Activity className="text-accent2" /> Global System Activity
            </h2>
            <ActivityFeed activities={data.recent_activity} />
          </div>
        </div>
      )}

    </div>
  );
};

export default Dashboard;
