import React, { createContext, useContext, useState, useEffect, type ReactNode } from 'react';

interface User {
  user_id: string;
  email: string;
  name: string;
  picture: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  handleOneTapSuccess: (credential: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Check for token in URL parameters (from OAuth callback)
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    
    if (tokenFromUrl) {
      login(tokenFromUrl);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      // Check for stored token
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        verifyToken(storedToken);
      }
    }
  }, []);

  const verifyToken = async (tokenToVerify: string) => {
    try {
      const response = await fetch(`http://localhost:8000/auth/verify?token=${tokenToVerify}`);
      if (response.ok) {
        const data = await response.json();
        setToken(tokenToVerify);
        setUser(data.user);
        localStorage.setItem('auth_token', tokenToVerify);
      } else {
        localStorage.removeItem('auth_token');
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('auth_token');
    }
  };

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('auth_token', newToken);
    
    // Decode token to get user info
    try {
      const payload = JSON.parse(atob(newToken.split('.')[1]));
      setUser(payload);
    } catch (error) {
      console.error('Failed to decode token:', error);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
  };

  const handleOneTapSuccess = async (credential: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/google/one-tap', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ credential }),
      });

      if (response.ok) {
        const data = await response.json();
        login(data.token);
      } else {
        console.error('One-tap authentication failed');
      }
    } catch (error) {
      console.error('One-tap authentication error:', error);
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, handleOneTapSuccess }}>
      {children}
    </AuthContext.Provider>
  );
};
