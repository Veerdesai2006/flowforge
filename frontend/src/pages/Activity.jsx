import React, { useState, useEffect } from 'react';
import api from '../api';
import { Loader2, Activity as ActivityIcon } from 'lucide-react';

export default function Activity() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivity = async () => {
      try {
        // We can just hit the dashboard endpoint again to get the recent_activity feed
        // since there's no dedicated GET /activities endpoint currently. 
        // In a real app we'd have a paginated /activities endpoint.
        const res = await api.get('/dashboard/super-admin');
        setActivities(res.data.recent_activity || []);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch activity");
      } finally {
        setLoading(false);
      }
    };
    fetchActivity();
  }, []);

  if (loading) return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin text-accent" /></div>;
  if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

  return (
    <div className="animate-fade-in pb-10 max-w-4xl mx-auto">
      <header className="mb-10 text-center">
        <h1 className="text-3xl font-black text-textMain mb-2">Global System Activity</h1>
        <p className="text-text2">View all actions taken across the entire platform.</p>
      </header>

      <div className="bg-bg2 p-8 rounded-2xl border border-border">
        {activities.length === 0 ? (
          <div className="text-center text-text3 italic py-10">No recent activity found.</div>
        ) : (
          <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-border before:to-transparent">
            {activities.map((act) => (
              <div key={act.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                <div className="flex items-center justify-center w-10 h-10 rounded-full border border-bg2 bg-accent2/20 text-accent2 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                  <ActivityIcon size={18} />
                </div>
                
                <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded border border-border bg-bg3 shadow">
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-bold text-textMain text-sm">{act.action}</div>
                    <time className="text-xs text-text3">{new Date(act.created_at).toLocaleString()}</time>
                  </div>
                  {act.description && <div className="text-sm text-text2">{act.description}</div>}
                  <div className="mt-3 inline-block px-2 py-1 bg-bg4 text-xs font-semibold text-text3 rounded-md">
                    User ID: {act.user_id}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
