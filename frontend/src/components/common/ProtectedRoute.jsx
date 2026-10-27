import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Loader from './Loader';

export const ProtectedRoute = ({ children, requiredRole }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader size="lg" message="Verifying session..." />
      </div>
    );
  }

  if (!user) {
    return <Navigate to={requiredRole === 'college' ? '/college/login' : '/student/login'} replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to={user.role === 'college' ? '/college/dashboard' : '/student/dashboard'} replace />;
  }

  return children;
};

export default ProtectedRoute;
