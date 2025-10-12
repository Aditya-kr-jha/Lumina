import { createContext, useState, useEffect, useContext } from 'react';
import { login as loginService, logout as logoutService, getUserProfile } from '../services/authService';
import { STORAGE_KEYS } from '../config/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN));
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const userData = await getUserProfile();
          setUser(userData);
        } catch (err) {
          console.error('Failed to fetch user profile:', err);
          // Token is invalid, clear it
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          setToken(null);
        }
      }
      setLoading(false);
    };

    initAuth();
  }, [token]);

  const login = async (username, password) => {
    try {
      setError(null);
      const data = await loginService(username, password);
      setToken(data.access_token);
      
      // Fetch user profile after login
      const userData = await getUserProfile();
      setUser(userData);
      
      return { success: true };
    } catch (err) {
      const errorMessage = err.message || 'Login failed';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    logoutService();
    setToken(null);
    setUser(null);
    window.location.href = '/';
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    logout,
    updateUser,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
