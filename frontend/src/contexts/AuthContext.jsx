// AuthContext.jsx
// Reason: Instead of passing user / token data through every component (prop drilling)
// Purpose: This file will store auth state in one place and makes it available everywhere

import React, { createContext, useState, useEffect, useCallback } from 'react';

/* eslint-disable react-refresh/only-export-components */
export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch user info from backend (wrapped in useCallback to fix dependency warning)
  const fetchUser = useCallback(async (authToken) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/auth/me', {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token invalid, clear it
        localStorage.removeItem('access_token');
        setToken(null);
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('access_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies needed

  // Check for token in localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem('access_token');
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setLoading(false);
    }
  }, [fetchUser]); // Now fetchUser is in dependency array

  // Login function
  const login = async (email, password) => {
    const response = await fetch('http://127.0.0.1:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    const accessToken = data.access_token;

    // Store token
    localStorage.setItem('access_token', accessToken);
    setToken(accessToken);

    // Fetch user info
    await fetchUser(accessToken);

    return data;
  };

  // Signup function
  const signup = async (email, username, password) => {
    const response = await fetch('http://127.0.0.1:8000/auth/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, username, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Signup failed');
    }

    const data = await response.json();
    const accessToken = data.access_token;

    // Store token
    localStorage.setItem('access_token', accessToken);
    setToken(accessToken);

    // Fetch user info
    await fetchUser(accessToken);

    return data;
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  const value = {
    user,
    token,
    loading,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    googleLogin: () => {
      // Redirect to backend OAuth endpoint
      window.location.href = 'http://127.0.0.1:8000/auth/google';
    }
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};