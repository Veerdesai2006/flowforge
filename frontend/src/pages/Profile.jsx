import React, { useState, useContext, useRef } from 'react';
import { Camera, Mail, Shield, CheckCircle, Loader2, Edit3, X } from 'lucide-react';
import api from '../api';
import { AuthContext } from '../contexts/AuthContext';

export default function Profile() {
  const { user, setUser } = useContext(AuthContext);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const [uploadError, setUploadError] = useState('');
  
  const [showEditModal, setShowEditModal] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [editData, setEditData] = useState({ first_name: '', last_name: '', email: '' });
  const [editError, setEditError] = useState('');

  const avatarInputRef = useRef(null);
  const bannerInputRef = useRef(null);

  const handleUpload = async (e, type) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setUploadMessage(`Uploading ${type}...`);
    setUploadError('');
    
    try {
      const res = await api.post(`/upload/${type}`, formData);
      setUser({ ...user, ...res.data });
      setUploadMessage('Upload successful!');
      setTimeout(() => setUploadMessage(''), 3000);
    } catch (err) {
      console.error(err);
      let errMsg = 'Upload failed.';
      if (err.response?.status === 400) errMsg = err.response.data.detail;
      if (err.response?.status === 413) errMsg = 'File is too large.';
      setUploadError(errMsg);
      setTimeout(() => setUploadError(''), 5000);
    } finally {
      setUploading(false);
      // Reset input so the same file can be uploaded again if needed
      e.target.value = null;
    }
  };

  const openEditModal = () => {
    setEditData({
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email
    });
    setEditError('');
    setShowEditModal(true);
  };

  const handleSaveProfile = async (e) => {
    e.preventDefault();
    setSavingProfile(true);
    setEditError('');
    
    try {
      const res = await api.patch('/users/me', editData);
      setUser(res.data);
      setShowEditModal(false);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 409) {
        setEditError('That email is already in use by another account.');
      } else if (err.response?.status === 400) {
        setEditError(err.response.data.detail || 'Invalid input.');
      } else {
        setEditError('An unexpected error occurred while saving.');
      }
    } finally {
      setSavingProfile(false);
    }
  };

  if (!user) return null;

  const initials = user.first_name[0] + user.last_name[0];

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-black text-textMain mb-8">My Profile</h1>

      <div className="bg-bg2 border border-border rounded-2xl overflow-hidden shadow-lg mb-8">
        {/* Banner */}
        <div className="h-48 relative group bg-gradient-to-r from-accent/20 to-accent2/20">
          {user.banner_url ? (
            <img src={`http://localhost:8000${user.banner_url}`} alt="Banner" className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-gradient-to-r from-accent/40 to-accent2/40"></div>
          )}
          <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <button onClick={() => bannerInputRef.current?.click()} className="flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-4 py-2 rounded-lg font-medium hover:bg-white/20 transition-colors">
              <Camera size={18} /> Change Banner
            </button>
          </div>
          <input type="file" ref={bannerInputRef} onChange={e => handleUpload(e, 'banner')} accept="image/*" className="hidden" />
        </div>

        {/* Profile Info */}
        <div className="px-8 pb-8 relative">
          <div className="flex justify-between items-end mb-6">
            <div className="-mt-16 relative group inline-block">
              <div className="w-32 h-32 rounded-full border-4 border-bg2 overflow-hidden bg-bg4 flex items-center justify-center text-4xl font-black text-accent2 shadow-xl">
                {user.avatar_url ? (
                  <img src={`http://localhost:8000${user.avatar_url}`} alt="Avatar" className="w-full h-full object-cover" />
                ) : initials.toUpperCase()}
              </div>
              <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity rounded-full flex items-center justify-center cursor-pointer border-4 border-transparent" onClick={() => avatarInputRef.current?.click()}>
                <Camera size={24} className="text-white" />
              </div>
              <input type="file" ref={avatarInputRef} onChange={e => handleUpload(e, 'avatar')} accept="image/*" className="hidden" />
            </div>
            
            <button 
              onClick={openEditModal}
              className="flex items-center gap-2 bg-bg3 hover:bg-bg4 text-textMain px-4 py-2 rounded-lg font-medium transition-colors border border-border"
            >
              <Edit3 size={18} /> Edit Profile
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h2 className="text-2xl font-bold text-textMain">{user.first_name} {user.last_name}</h2>
              <div className="flex items-center gap-4 mt-2 text-sm text-text2">
                <span className="flex items-center gap-1.5"><Mail size={16} /> {user.email}</span>
                <span className="flex items-center gap-1.5"><Shield size={16} /> {user.role}</span>
                {user.is_verified && <span className="flex items-center gap-1.5 text-green"><CheckCircle size={16} /> Verified</span>}
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Upload Feedback Toasts */}
      {(uploading || uploadMessage) && (
        <div className="fixed bottom-4 right-4 bg-accent text-white px-4 py-3 rounded-lg shadow-xl flex items-center gap-3">
          {uploading ? <Loader2 size={18} className="animate-spin" /> : <CheckCircle size={18} />} 
          <span className="font-medium">{uploadMessage}</span>
        </div>
      )}
      
      {uploadError && (
        <div className="fixed bottom-4 right-4 bg-red text-white px-4 py-3 rounded-lg shadow-xl flex items-center gap-3">
          <span className="font-medium">{uploadError}</span>
          <button onClick={() => setUploadError('')} className="ml-2 hover:bg-white/20 p-1 rounded"><X size={16} /></button>
        </div>
      )}

      {/* EDIT PROFILE MODAL */}
      {showEditModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-bg2 border border-border rounded-2xl w-full max-w-md p-6 shadow-2xl">
            <h2 className="text-xl font-bold mb-6 text-textMain">Edit Profile</h2>
            
            {editError && (
              <div className="bg-red/10 border border-red/30 text-red px-4 py-3 rounded-lg mb-6 text-sm">
                {editError}
              </div>
            )}
            
            <form onSubmit={handleSaveProfile}>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">First Name</label>
                <input 
                  required 
                  value={editData.first_name} 
                  onChange={e => setEditData({...editData, first_name: e.target.value})} 
                  className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" 
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Last Name</label>
                <input 
                  required 
                  value={editData.last_name} 
                  onChange={e => setEditData({...editData, last_name: e.target.value})} 
                  className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" 
                />
              </div>
              <div className="mb-8">
                <label className="block text-sm font-semibold text-text2 mb-1.5">Email</label>
                <input 
                  required 
                  type="email"
                  value={editData.email} 
                  onChange={e => setEditData({...editData, email: e.target.value})} 
                  className="w-full bg-bg3 border border-border rounded-lg px-4 py-2.5 text-textMain focus:border-accent focus:ring-1 focus:ring-accent outline-none" 
                />
              </div>
              <div className="flex justify-end gap-3">
                <button 
                  type="button" 
                  onClick={() => setShowEditModal(false)} 
                  disabled={savingProfile}
                  className="px-4 py-2 rounded-lg font-medium text-text2 hover:bg-bg3 border border-transparent disabled:opacity-50 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={savingProfile}
                  className="bg-accent text-white px-4 py-2 rounded-lg font-medium hover:bg-[#5b4cdb] flex items-center gap-2 disabled:opacity-70 transition-colors"
                >
                  {savingProfile ? <><Loader2 size={16} className="animate-spin" /> Saving...</> : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
