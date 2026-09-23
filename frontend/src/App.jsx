import React, { useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './contexts/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Topics from './pages/Topics';
import Boards from './pages/Boards';
import Tasks from './pages/Tasks';
import Profile from './pages/Profile';
import Users from './pages/Users';
import Admins from './pages/Admins';
import Activity from './pages/Activity';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);
  if (loading) return <div className="min-h-screen flex items-center justify-center bg-bg text-textMain">Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return children;
};

import ErrorBoundary from './components/ErrorBoundary';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route index element={<Topics />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="users" element={<Users />} />
        <Route path="admins" element={<Admins />} />
        <Route path="activity" element={<Activity />} />
        <Route path="projects/:projectId/boards" element={<Boards />} />
        <Route path="boards/:boardId/tasks" element={<Tasks />} />
        <Route path="profile" element={<Profile />} />
      </Route>
    </Routes>
  );
};

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;
