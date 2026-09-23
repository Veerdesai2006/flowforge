import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, Loader2, ArrowRight, Edit2, Trash2 } from 'lucide-react';
import api from '../api';
import { AuthContext } from '../contexts/AuthContext';

export default function Topics() {
  const { user } = useContext(AuthContext);
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Create State
  const [showModal, setShowModal] = useState(false);
  const [newTopic, setNewTopic] = useState({ name: '', description: '' });

  // Edit State
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTopic, setEditingTopic] = useState({ id: null, name: '', description: '' });

  const fetchTopics = async () => {
    try {
      const res = await api.get('/projects');
      setTopics(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/projects', newTopic);
      setShowModal(false);
      setNewTopic({ name: '', description: '' });
      fetchTopics();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/projects/${editingTopic.id}`, { name: editingTopic.name, description: editingTopic.description });
      setShowEditModal(false);
      fetchTopics();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to delete this Topic? All boards and tasks inside will be lost.")) return;
    try {
      await api.delete(`/projects/${id}`);
      fetchTopics();
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (e, topic) => {
    e.preventDefault();
    e.stopPropagation();
    setEditingTopic(topic);
    setShowEditModal(true);
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  if (loading) return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin text-accent" /></div>;

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black text-textMain">{getGreeting()}, {user?.first_name} 👋</h1>
          <p className="text-text2 mt-1">Here are your Topics</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 bg-accent hover:bg-[#5b4cdb] text-white px-4 py-2 rounded-lg font-medium transition-all shadow-[0_4px_12px_rgba(108,92,231,0.3)]">
          <PlusCircle size={18} /> New Topic
        </button>
      </div>

      {topics.length === 0 ? (
        <div className="text-center py-20 bg-bg3 border border-border rounded-xl">
          <div className="text-text3 mb-4"><PlusCircle size={48} className="mx-auto opacity-50" /></div>
          <h3 className="text-lg font-bold text-textMain">No Topics yet</h3>
          <p className="text-text2 mb-6 text-sm">Create your first Topic to start organizing your work.</p>
          <button onClick={() => setShowModal(true)} className="bg-accent text-white px-5 py-2 rounded-lg font-medium">Create Topic</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics.map((t, i) => {
            const colors = ['#6c5ce7', '#00b894', '#fdcb6e', '#0984e3', '#ff6b6b', '#a29bfe'];
            const color = colors[i % colors.length];
            return (
              <Link to={`/projects/${t.id}/boards`} key={t.id} className="group bg-bg3 border border-border rounded-xl p-6 transition-all hover:-translate-y-1 hover:border-accent/40 hover:shadow-[0_8px_30px_rgba(0,0,0,0.5)] flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold" style={{ background: color }}>
                    {t.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={(e) => openEditModal(e, t)} className="p-2 text-text3 hover:text-accent transition-colors bg-bg4 rounded-md">
                      <Edit2 size={16} />
                    </button>
                    <button onClick={(e) => handleDelete(e, t.id)} className="p-2 text-text3 hover:text-red transition-colors bg-bg4 rounded-md">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                <h3 className="font-bold text-textMain text-lg mb-2">{t.name}</h3>
                <p className="text-text2 text-sm line-clamp-2 min-h-[40px] mb-4 flex-1">
                  {t.description || <span className="italic opacity-70">No description</span>}
                </p>
                <div className="flex items-center justify-between text-sm pt-4 border-t border-border mt-auto">
                  <span className="text-accent2 font-medium bg-accent2/10 px-2 py-1 rounded-md">Boards</span>
                  <ArrowRight size={16} className="text-text3 group-hover:text-accent transition-colors" />
                </div>
              </Link>
            )
          })}
        </div>
      )}

      {/* CREATE MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg2 border border-border rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Create New Topic</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Name</label>
                <input required value={newTopic.name} onChange={e => setNewTopic({...newTopic, name: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" placeholder="e.g. Mobile App" />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Description (optional)</label>
                <textarea value={newTopic.description} onChange={e => setNewTopic({...newTopic, description: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none h-24" placeholder="What is this topic about?" />
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 rounded-lg font-medium text-text2 hover:bg-bg3 border border-transparent">Cancel</button>
                <button type="submit" className="bg-accent text-white px-4 py-2 rounded-lg font-medium hover:bg-[#5b4cdb]">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* EDIT MODAL */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg2 border border-border rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Edit Topic</h2>
            <form onSubmit={handleUpdate}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Name</label>
                <input required value={editingTopic.name} onChange={e => setEditingTopic({...editingTopic, name: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Description</label>
                <textarea value={editingTopic.description || ''} onChange={e => setEditingTopic({...editingTopic, description: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none h-24" />
              </div>
              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowEditModal(false)} className="px-4 py-2 rounded-lg font-medium text-text2 hover:bg-bg3 border border-transparent">Cancel</button>
                <button type="submit" className="bg-accent text-white px-4 py-2 rounded-lg font-medium hover:bg-[#5b4cdb]">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
