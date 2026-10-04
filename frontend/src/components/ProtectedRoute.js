import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ user, children, requiredRole, loading = false }) => {
  if (loading || (!user && localStorage.getItem("token"))) return null;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const allowedRoles = Array.isArray(requiredRole) ? requiredRole : [requiredRole];
  if (requiredRole && !allowedRoles.includes(user.userType)) {
    return <Navigate to={user.userType === "artisan" ? "/artisan" : "/"} replace />;
  }

  return children;
};

export default ProtectedRoute;