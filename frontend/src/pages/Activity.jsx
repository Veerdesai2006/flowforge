import React, { useState, useEffect } from 'react';
import api from '../api';
import { Loader2 } from 'lucide-react';
import ActivityFeed from '../components/ActivityFeed';

export default function Activity() {
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchActivity = async () => {
      try {
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

      <ActivityFeed 
        activities={activities}
        pageSize={10}
        maxHeight="600px"
      />
    </div>
  );
}

