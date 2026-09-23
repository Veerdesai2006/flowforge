import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { PlusCircle, Loader2, ArrowLeft, Trash2, Edit2 } from 'lucide-react';
import api from '../api';

export default function Boards() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [boards, setBoards] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Create State
  const [showModal, setShowModal] = useState(false);
  const [newBoard, setNewBoard] = useState({ name: '', description: '' });

  // Edit State
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingBoard, setEditingBoard] = useState({ id: null, name: '', description: '' });

  const fetchBoards = async () => {
    try {
      const res = await api.get(`/boards/project/${projectId}`);
      setBoards(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoards();
  }, [projectId]);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/boards', { ...newBoard, project_id: parseInt(projectId) });
      setShowModal(false);
      setNewBoard({ name: '', description: '' });
      fetchBoards();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/boards/${editingBoard.id}`, { name: editingBoard.name, description: editingBoard.description });
      setShowEditModal(false);
      fetchBoards();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (e, id) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm('Delete this board? All tasks inside will be lost.')) return;
    try {
      await api.delete(`/boards/${id}`);
      fetchBoards();
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (e, board) => {
    e.preventDefault();
    e.stopPropagation();
    setEditingBoard(board);
    setShowEditModal(true);
  };

  if (loading) return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin text-accent" /></div>;

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <button onClick={() => navigate('/')} className="text-text3 hover:text-textMain transition-colors"><ArrowLeft size={20} /></button>
        <span className="text-sm font-semibold text-text3 tracking-wider uppercase">Topic Boards</span>
      </div>

      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-black text-textMain">Boards</h1>
          <p className="text-text2 mt-1">Manage boards for this topic</p>
        </div>
        <button onClick={() => setShowModal(true)} className="flex items-center gap-2 bg-accent hover:bg-[#5b4cdb] text-white px-4 py-2 rounded-lg font-medium transition-all shadow-[0_4px_12px_rgba(108,92,231,0.3)]">
          <PlusCircle size={18} /> New Board
        </button>
      </div>

      {boards.length === 0 ? (
        <div className="text-center py-20 bg-bg3 border border-border rounded-xl">
          <div className="text-text3 mb-4"><PlusCircle size={48} className="mx-auto opacity-50" /></div>
          <h3 className="text-lg font-bold text-textMain">No Boards yet</h3>
          <p className="text-text2 mb-6 text-sm">Create a board to start managing tasks.</p>
          <button onClick={() => setShowModal(true)} className="bg-accent text-white px-5 py-2 rounded-lg font-medium">Create Board</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {boards.map((b, i) => {
            const colors = ['#00b894', '#6c5ce7', '#0984e3', '#fdcb6e', '#ff6b6b'];
            const color = colors[i % colors.length];
            return (
              <Link to={`/boards/${b.id}/tasks`} key={b.id} className="group bg-bg3 border border-border rounded-xl p-6 transition-all hover:-translate-y-1 hover:border-accent/40 hover:shadow-[0_8px_30px_rgba(0,0,0,0.5)] flex flex-col h-full">
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold" style={{ background: color }}>
                    {b.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={(e) => openEditModal(e, b)} className="p-2 text-text3 hover:text-accent transition-colors bg-bg4 rounded-md">
                      <Edit2 size={16} />
                    </button>
                    <button onClick={(e) => handleDelete(e, b.id)} className="p-2 text-text3 hover:text-red transition-colors bg-bg4 rounded-md">
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
                <h3 className="font-bold text-textMain text-lg mb-2">{b.name}</h3>
                <p className="text-text2 text-sm line-clamp-2 min-h-[40px] mb-4 flex-1">
                  {b.description || <span className="italic opacity-70">No description</span>}
                </p>
                <div className="flex justify-end pt-4 border-t border-border mt-auto">
                  <span className="text-accent2 text-xs font-semibold">Click to open tasks &rarr;</span>
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
            <h2 className="text-xl font-bold mb-4">Create New Board</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Name</label>
                <input required value={newBoard.name} onChange={e => setNewBoard({...newBoard, name: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" placeholder="e.g. Sprint 1" />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Description (optional)</label>
                <textarea value={newBoard.description} onChange={e => setNewBoard({...newBoard, description: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none h-24" placeholder="What will this board track?" />
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
            <h2 className="text-xl font-bold mb-4">Edit Board</h2>
            <form onSubmit={handleUpdate}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Name</label>
                <input required value={editingBoard.name} onChange={e => setEditingBoard({...editingBoard, name: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Description</label>
                <textarea value={editingBoard.description || ''} onChange={e => setEditingBoard({...editingBoard, description: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none h-24" />
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
