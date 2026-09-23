import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { ArrowLeft, PlusCircle, Loader2, Trash2, Edit2, ChevronLeft, ChevronRight } from 'lucide-react';
import api from '../api';

const STATUSES = {
  TODO: { name: 'To Do / Postponed', color: 'bg-text3' },
  IN_PROGRESS: { name: 'Running', color: 'bg-yellow' },
  DONE: { name: 'Completed', color: 'bg-green' }
};

export default function Tasks() {
  const { boardId } = useParams();
  const navigate = useNavigate();
  
  // Independent Column Data
  const [tasks, setTasks] = useState({ TODO: [], IN_PROGRESS: [], DONE: [] });
  
  // Pagination State per column
  const [pages, setPages] = useState({ TODO: 1, IN_PROGRESS: 1, DONE: 1 });
  const [totalItems, setTotalItems] = useState({ TODO: 0, IN_PROGRESS: 0, DONE: 0 });
  const [totalPages, setTotalPages] = useState({ TODO: 1, IN_PROGRESS: 1, DONE: 1 });
  
  // Global page size
  const [pageSize, setPageSize] = useState(10);
  
  const [loading, setLoading] = useState(true);
  const [columnLoading, setColumnLoading] = useState({ TODO: false, IN_PROGRESS: false, DONE: false });
  
  // Create/Edit Modals
  const [showModal, setShowModal] = useState(false);
  const [newTask, setNewTask] = useState({ title: '', description: '', priority: 'MEDIUM' });
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTask, setEditingTask] = useState({ id: null, title: '', description: '', priority: 'MEDIUM', status: 'TODO' });

  // Fetch a single column's data with pagination
  const fetchColumn = async (statusKey, pageNum) => {
    setColumnLoading(prev => ({ ...prev, [statusKey]: true }));
    try {
      const res = await api.get(`/tasks/board/${boardId}?status=${statusKey}&page=${pageNum}&page_size=${pageSize}`);
      
      setTasks(prev => ({ ...prev, [statusKey]: res.data.items }));
      setTotalItems(prev => ({ ...prev, [statusKey]: res.data.total_items }));
      setTotalPages(prev => ({ ...prev, [statusKey]: res.data.total_pages }));
    } catch (err) {
      console.error(`Failed to fetch ${statusKey} tasks:`, err);
    } finally {
      setColumnLoading(prev => ({ ...prev, [statusKey]: false }));
    }
  };

  // Fetch all columns
  const fetchAllTasks = async () => {
    setLoading(true);
    await Promise.all([
      fetchColumn('TODO', pages.TODO),
      fetchColumn('IN_PROGRESS', pages.IN_PROGRESS),
      fetchColumn('DONE', pages.DONE)
    ]);
    setLoading(false);
  };

  useEffect(() => {
    fetchAllTasks();
  }, [boardId, pageSize]); // Refetch if page_size changes

  // Triggered when a user clicks Next/Previous on a column
  const handlePageChange = (statusKey, newPage) => {
    if (newPage < 1 || newPage > totalPages[statusKey]) return;
    setPages(prev => ({ ...prev, [statusKey]: newPage }));
    fetchColumn(statusKey, newPage);
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/tasks', { ...newTask, board_id: parseInt(boardId) });
      setShowModal(false);
      setNewTask({ title: '', description: '', priority: 'MEDIUM' });
      // New tasks always go to TODO. We should refresh the TODO column at page 1.
      setPages(prev => ({ ...prev, TODO: 1 }));
      fetchColumn('TODO', 1);
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    try {
      await api.patch(`/tasks/${editingTask.id}`, { 
        title: editingTask.title, 
        description: editingTask.description,
        priority: editingTask.priority
      });
      setShowEditModal(false);
      fetchColumn(editingTask.status, pages[editingTask.status]);
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (id, statusKey) => {
    if (!window.confirm('Delete task?')) return;
    try {
      await api.delete(`/tasks/${id}`);
      
      // If we delete the last item on the page, and we are not on page 1, go back one page.
      if (tasks[statusKey].length === 1 && pages[statusKey] > 1) {
        setPages(prev => ({ ...prev, [statusKey]: pages[statusKey] - 1 }));
        fetchColumn(statusKey, pages[statusKey] - 1);
      } else {
        fetchColumn(statusKey, pages[statusKey]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const openEditModal = (task) => {
    setEditingTask(task);
    setShowEditModal(true);
  };

  const onDragEnd = async (result) => {
    const { source, destination, draggableId } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    const startCol = source.droppableId;
    const endCol = destination.droppableId;

    // Optimistic UI update for drag within same column
    if (startCol === endCol) {
      const newCol = [...tasks[startCol]];
      const [removed] = newCol.splice(source.index, 1);
      newCol.splice(destination.index, 0, removed);
      setTasks(prev => ({ ...prev, [startCol]: newCol }));
      // We don't actually persist index ordering yet, so backend update is unnecessary for same-col drag
      return;
    }

    // Moving across columns
    try {
      // 1. Instantly update backend
      await api.patch(`/tasks/${draggableId}`, { status: endCol });
      
      // 2. Refresh both columns from backend to guarantee pagination integrity.
      // E.g. moving a task out of TODO might pull a task from page 2 of TODO onto page 1.
      fetchColumn(startCol, pages[startCol]);
      fetchColumn(endCol, pages[endCol]);
    } catch (err) {
      console.error("Failed to move task", err);
      // Revert optimism if failed
      fetchColumn(startCol, pages[startCol]);
      fetchColumn(endCol, pages[endCol]);
    }
  };

  if (loading) return <div className="flex h-64 items-center justify-center"><Loader2 className="animate-spin text-accent" /></div>;

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)] md:h-[calc(100vh-4rem)] -m-4 md:-m-8 p-4 md:p-8 overflow-hidden">
      <div className="flex items-center gap-3 mb-6 shrink-0">
        <button onClick={() => navigate(-1)} className="text-text3 hover:text-textMain transition-colors"><ArrowLeft size={20} /></button>
        <span className="text-sm font-semibold text-text3 tracking-wider uppercase">Kanban Board</span>
      </div>

      <div className="flex justify-between items-center mb-8 shrink-0">
        <div>
          <h1 className="text-3xl font-black text-textMain">Tasks</h1>
          <p className="text-text2 mt-1">Drag and drop to update status</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm text-text2">Tasks per page:</label>
            <select 
              value={pageSize} 
              onChange={e => {
                setPageSize(Number(e.target.value));
                setPages({ TODO: 1, IN_PROGRESS: 1, DONE: 1 }); // Reset all pages when changing size
              }} 
              className="bg-bg3 border border-border rounded-lg px-2 py-1 text-sm text-textMain focus:border-accent outline-none"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={30}>30</option>
            </select>
          </div>
          <button onClick={() => setShowModal(true)} className="flex items-center gap-2 bg-accent hover:bg-[#5b4cdb] text-white px-4 py-2 rounded-lg font-medium transition-all shadow-[0_4px_12px_rgba(108,92,231,0.3)]">
            <PlusCircle size={18} /> Add Task
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-x-auto pb-4">
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="flex gap-6 items-start h-full min-w-max">
            {Object.entries(STATUSES).map(([statusKey, statusMeta]) => (
              <div key={statusKey} className="w-80 flex flex-col bg-bg2 border border-border rounded-xl h-full max-h-full">
                
                {/* Column Header */}
                <div className="p-4 border-b border-border flex items-center justify-between bg-white/[0.02] rounded-t-xl shrink-0">
                  <div className="flex items-center gap-2 font-bold text-sm">
                    <div className={`w-2.5 h-2.5 rounded-full ${statusMeta.color}`}></div>
                    {statusMeta.name}
                  </div>
                  <span className="bg-bg4 text-text2 text-xs font-semibold px-2 py-0.5 rounded-full">
                    {totalItems[statusKey]} total
                  </span>
                </div>
                
                {/* Column Body */}
                <Droppable droppableId={statusKey}>
                  {(provided, snapshot) => (
                    <div 
                      ref={provided.innerRef} 
                      {...provided.droppableProps}
                      className={`flex-1 p-3 overflow-y-auto min-h-[150px] transition-colors relative ${snapshot.isDraggingOver ? 'bg-white/[0.02]' : ''}`}
                    >
                      {columnLoading[statusKey] ? (
                        <div className="absolute inset-0 flex items-center justify-center bg-bg2/50 backdrop-blur-sm z-10">
                          <Loader2 className="animate-spin text-accent" />
                        </div>
                      ) : null}

                      {tasks[statusKey].map((task, index) => (
                        <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`group bg-bg3 border rounded-xl p-4 mb-3 transition-shadow ${snapshot.isDragging ? 'shadow-[0_8px_30px_rgba(0,0,0,0.5)] border-accent' : 'border-border shadow-sm hover:border-accent/40 hover:-translate-y-0.5 hover:shadow-md'}`}
                            >
                              <div className="flex justify-between items-start mb-2">
                                <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${
                                  task.priority === 'HIGH' ? 'bg-red/20 text-red' : 
                                  task.priority === 'LOW' ? 'bg-cyan/20 text-cyan' : 'bg-yellow/20 text-yellow'
                                }`}>
                                  {task.priority}
                                </span>
                                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity -mr-2 -mt-2">
                                  <button onClick={() => openEditModal(task)} className="text-text3 hover:text-accent transition-colors p-1 bg-bg4 rounded">
                                    <Edit2 size={14} />
                                  </button>
                                  <button onClick={() => handleDelete(task.id, statusKey)} className="text-text3 hover:text-red transition-colors p-1 bg-bg4 rounded">
                                    <Trash2 size={14} />
                                  </button>
                                </div>
                              </div>
                              <h4 className="font-bold text-sm mb-1 text-textMain">{task.title}</h4>
                              {task.description && <p className="text-xs text-text2 line-clamp-3 leading-relaxed">{task.description}</p>}
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                    </div>
                  )}
                </Droppable>

                {/* Column Pagination Controls */}
                {totalItems[statusKey] > 0 && (
                  <div className="p-3 border-t border-border flex items-center justify-between shrink-0 bg-white/[0.01] rounded-b-xl">
                    <button 
                      onClick={() => handlePageChange(statusKey, pages[statusKey] - 1)}
                      disabled={pages[statusKey] === 1 || columnLoading[statusKey]}
                      className="p-1 rounded-md text-text2 hover:text-textMain disabled:opacity-30 disabled:hover:text-text2 transition-colors"
                    >
                      <ChevronLeft size={18} />
                    </button>
                    <span className="text-xs font-semibold text-text3">
                      Page {pages[statusKey]} of {totalPages[statusKey]}
                    </span>
                    <button 
                      onClick={() => handlePageChange(statusKey, pages[statusKey] + 1)}
                      disabled={pages[statusKey] === totalPages[statusKey] || columnLoading[statusKey]}
                      className="p-1 rounded-md text-text2 hover:text-textMain disabled:opacity-30 disabled:hover:text-text2 transition-colors"
                    >
                      <ChevronRight size={18} />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </DragDropContext>
      </div>

      {/* CREATE MODAL */}
      {showModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg2 border border-border rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-4">Create New Task</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Title</label>
                <input required value={newTask.title} onChange={e => setNewTask({...newTask, title: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" placeholder="Task name..." />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Description</label>
                <textarea value={newTask.description} onChange={e => setNewTask({...newTask, description: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none h-24" placeholder="Details..." />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Priority</label>
                <select value={newTask.priority} onChange={e => setNewTask({...newTask, priority: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent outline-none">
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
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
            <h2 className="text-xl font-bold mb-4">Edit Task</h2>
            <form onSubmit={handleUpdate}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Title</label>
                <input required value={editingTask.title} onChange={e => setEditingTask({...editingTask, title: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Description</label>
                <textarea value={editingTask.description || ''} onChange={e => setEditingTask({...editingTask, description: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none h-24" />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Priority</label>
                <select value={editingTask.priority} onChange={e => setEditingTask({...editingTask, priority: e.target.value})} className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent outline-none">
                  <option value="LOW">Low</option>
                  <option value="MEDIUM">Medium</option>
                  <option value="HIGH">High</option>
                </select>
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
