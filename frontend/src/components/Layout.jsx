import React, { useContext } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { LayoutDashboard, User, LogOut, ArrowLeft, PlusCircle } from 'lucide-react';

const Layout = () => {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();

  if (!user) return null;

  return (
    <div className="flex min-h-screen bg-bg text-textMain">
      {/* Sidebar */}
      <aside className="w-56 bg-bg2 border-r border-border p-5 flex flex-col gap-1 flex-shrink-0 hidden md:flex">
        <div className="text-xl font-black bg-gradient-to-br from-accent to-accent2 bg-clip-text text-transparent mb-6 px-2">
          FlowForge
        </div>

        {/* Dashboard Link (All Roles) */}
        <Link to="/dashboard" className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === '/dashboard' ? 'bg-bg4 text-accent2' : 'text-text2 hover:bg-bg4 hover:text-textMain'}`}>
          <LayoutDashboard size={18} /> Dashboard
        </Link>
        
        {/* Users Link (ADMIN & SUPER_ADMIN) */}
        {(user.role === 'ADMIN' || user.role === 'SUPER_ADMIN') && (
          <Link to="/users" className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === '/users' ? 'bg-bg4 text-accent2' : 'text-text2 hover:bg-bg4 hover:text-textMain'}`}>
            <User size={18} /> Users
          </Link>
        )}

        {/* Admins & Activity Links (SUPER_ADMIN ONLY) */}
        {user.role === 'SUPER_ADMIN' && (
          <>
            <Link to="/admins" className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === '/admins' ? 'bg-bg4 text-accent2' : 'text-text2 hover:bg-bg4 hover:text-textMain'}`}>
              <User size={18} /> Admins
            </Link>
            <Link to="/activity" className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === '/activity' ? 'bg-bg4 text-accent2' : 'text-text2 hover:bg-bg4 hover:text-textMain'}`}>
              <LayoutDashboard size={18} /> Activity
            </Link>
          </>
        )}

        {/* Topics & Profile (All Roles) */}
        <Link to="/" className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === '/' || location.pathname.startsWith('/projects') ? 'bg-bg4 text-accent2' : 'text-text2 hover:bg-bg4 hover:text-textMain'}`}>
          <PlusCircle size={18} /> Topics
        </Link>
        <Link to="/profile" className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${location.pathname === '/profile' ? 'bg-bg4 text-accent2' : 'text-text2 hover:bg-bg4 hover:text-textMain'}`}>
          <User size={18} /> My Profile
        </Link>

        <div className="mt-4 mb-2 px-3 text-[10px] font-bold tracking-widest uppercase text-text3">Account</div>
        <button onClick={logout} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-text2 hover:bg-bg4 hover:text-textMain text-left transition-colors w-full">
          <LogOut size={18} /> Logout
        </button>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-4 md:p-8">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
