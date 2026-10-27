import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('auth_user');
      return saved ? JSON.parse(saved) : null;
    } catch (err) {
      return null;
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const res = await api.get('/auth/me');
          if (isMounted) {
            setUser(res.data.user);
            localStorage.setItem('auth_user', JSON.stringify(res.data.user));
          }
        } catch (err) {
          if (isMounted) {
            if (err.response && (err.response.status === 401 || err.response.status === 403)) {
              localStorage.removeItem('auth_token');
              localStorage.removeItem('auth_user');
              setUser(null);
            }
          }
        }
      }
      if (isMounted) {
        setLoading(false);
      }
    };

    checkAuth();
    return () => {
      isMounted = false;
    };
  }, []);

  const loginStudent = async (email, password) => {
    const res = await api.post('/auth/student/login', { email, password });
    localStorage.setItem('auth_token', res.data.token);
    localStorage.setItem('auth_user', JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data;
  };

  const registerStudent = async (data) => {
    const res = await api.post('/auth/student/register', data);
    localStorage.setItem('auth_token', res.data.token);
    localStorage.setItem('auth_user', JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data;
  };

  const loginCollege = async (email, password) => {
    const res = await api.post('/auth/college/login', { email, password });
    localStorage.setItem('auth_token', res.data.token);
    localStorage.setItem('auth_user', JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data;
  };

  const registerCollege = async (data) => {
    const res = await api.post('/auth/college/register', data);
    localStorage.setItem('auth_token', res.data.token);
    localStorage.setItem('auth_user', JSON.stringify(res.data.user));
    setUser(res.data.user);
    return res.data;
  };

  // Unified login handler supporting (email, password, role)
  const login = async (email, password, role = 'student') => {
    const roleLower = (role || 'student').toLowerCase();
    if (roleLower === 'college' || roleLower === 'institution') {
      return await loginCollege(email, password);
    } else if (roleLower === 'student') {
      return await loginStudent(email, password);
    } else {
      const res = await api.post('/auth/login', { email, password, role });
      localStorage.setItem('auth_token', res.data.token);
      localStorage.setItem('auth_user', JSON.stringify(res.data.user));
      setUser(res.data.user);
      return res.data;
    }
  };

  // Unified register handler supporting (data)
  const register = async (data) => {
    const roleLower = (data?.role || 'student').toLowerCase();
    if (roleLower === 'college' || roleLower === 'institution') {
      return await registerCollege(data);
    } else if (roleLower === 'student') {
      return await registerStudent(data);
    } else {
      const res = await api.post('/auth/register', data);
      localStorage.setItem('auth_token', res.data.token);
      localStorage.setItem('auth_user', JSON.stringify(res.data.user));
      setUser(res.data.user);
      return res.data;
    }
  };

  const logout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
    setUser(null);
  };

  const updateProfile = (updatedUser) => {
    setUser(updatedUser);
    localStorage.setItem('auth_user', JSON.stringify(updatedUser));
  };

  const role = (user?.role || user?.role_raw || '').toLowerCase();

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        loginStudent,
        registerStudent,
        loginCollege,
        registerCollege,
        logout,
        updateProfile,
        isStudent: role === 'student',
        isCollege: role === 'college' || role === 'institution'
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthContext;
